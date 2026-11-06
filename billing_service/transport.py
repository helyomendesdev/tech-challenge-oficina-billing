import json
import logging
import re
from contextlib import contextmanager

import boto3
from botocore.config import Config

from billing_service.config import Settings
from billing_service.domain import BillingError
from billing_service.service import Billing

LOG = logging.getLogger("billing")


def trace_attributes(headers: dict) -> dict:
    trace = headers.get("traceparent", "")
    if not re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}", trace):
        return {}
    if trace[3:35] == "0" * 32 or trace[36:52] == "0" * 16:
        return {}
    result = {"traceparent": {"DataType": "String", "StringValue": trace}}
    state = headers.get("tracestate", "")
    if state and len(state) <= 512 and all(32 <= ord(c) <= 126 for c in state):
        result["tracestate"] = {"DataType": "String", "StringValue": state}
    return result


@contextmanager
def background_task(name: str, headers: dict | None = None):
    """Run the block as a New Relic background transaction; no-op without the agent."""
    try:
        import newrelic.agent as agent

        app = agent.application()
    except Exception:
        app = None
    if app is None:
        yield
        return
    with agent.BackgroundTask(app, name=name, group="Message/SQS"):
        if headers:
            agent.accept_distributed_trace_headers(headers, transport_type="Queue")
        yield


def sqs_client(settings: Settings):
    return boto3.client(
        "sqs",
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
        config=Config(connect_timeout=5, read_timeout=25, retries={"max_attempts": 2}),
    )


class SQSPublisher:
    def __init__(self, client, queue_url: str):
        if not queue_url:
            raise ValueError("QUEUE_OS_SAGA_RESPOSTAS_URL is required")
        self.client, self.queue_url = client, queue_url

    def publish(self, message: dict, attributes: dict) -> None:
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            MessageGroupId=message["sagaId"],
            MessageDeduplicationId=message["messageId"],
            MessageAttributes=attributes,
        )


class SQSConsumer:
    def __init__(self, client, queue_url: str, billing: Billing):
        if not queue_url:
            raise ValueError("QUEUE_BILLING_COMANDOS_URL is required")
        self.client, self.queue_url, self.billing = client, queue_url, billing

    def once(self) -> int:
        batch = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10,
            VisibilityTimeout=60,
            MessageAttributeNames=["All"],
        )
        count = 0
        for item in batch.get("Messages", []):
            try:
                body = json.loads(item["Body"])
                headers = {
                    k: v.get("StringValue", "")
                    for k, v in item.get("MessageAttributes", {}).items()
                }
                name = body.get("type") if isinstance(body, dict) else None
                carried = {k: v for k, v in headers.items() if k in ("traceparent", "tracestate")}
                with background_task(name or "SQSConsumer", carried):
                    self.billing.handle(body, trace_attributes(headers))
                self.client.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=item["ReceiptHandle"]
                )
                count += 1
            except Exception as exc:
                LOG.warning(
                    "sqs_command_not_acknowledged",
                    extra={
                        "code": exc.code if isinstance(exc, BillingError) else type(exc).__name__
                    },
                )
                break  # Do not pass a failed item in the FIFO group in this batch.
        return count
