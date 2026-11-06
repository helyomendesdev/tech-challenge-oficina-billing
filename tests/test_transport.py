import json

import boto3
import pytest
from moto import mock_aws

from billing_service.config import Settings
from billing_service.transport import SQSConsumer, SQSPublisher, sqs_client, trace_attributes
from billing_service.workers import relay_once
from tests.test_billing import generated

TRACE = "00-" + "1" * 32 + "-" + "2" * 16 + "-01"


def test_trace_attributes_reject_invalid_and_never_publish_auth():
    assert not trace_attributes({"traceparent": "bad"})
    assert not trace_attributes({"traceparent": "00-" + "0" * 32 + "-" + "2" * 16 + "-01"})
    attrs = trace_attributes(
        {"traceparent": TRACE, "tracestate": "vendor=value", "Authorization": "secret"}
    )
    assert set(attrs) == {"traceparent", "tracestate"}
    assert "tracestate" not in trace_attributes({"traceparent": TRACE, "tracestate": "x" * 513})


@mock_aws
def test_consumer_fifo_ack_and_outbox_correlation(billing, db, generate, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    client = sqs_client(Settings())
    queue = client.create_queue(QueueName="billing.fifo", Attributes={"FifoQueue": "true"})[
        "QueueUrl"
    ]
    responses = client.create_queue(QueueName="responses.fifo", Attributes={"FifoQueue": "true"})[
        "QueueUrl"
    ]
    attrs = trace_attributes({"traceparent": TRACE})
    client.send_message(
        QueueUrl=queue,
        MessageBody=json.dumps(generate),
        MessageAttributes=attrs,
        MessageGroupId=generate["sagaId"],
        MessageDeduplicationId=generate["messageId"],
    )
    consumer = SQSConsumer(client, queue, billing)
    assert consumer.once() == 1
    assert (
        client.get_queue_attributes(QueueUrl=queue, AttributeNames=["ApproximateNumberOfMessages"])[
            "Attributes"
        ]["ApproximateNumberOfMessages"]
        == "0"
    )
    assert relay_once(db, SQSPublisher(client, responses))
    response = client.receive_message(
        QueueUrl=responses, MessageAttributeNames=["All"], AttributeNames=["All"]
    )["Messages"][0]
    body = json.loads(response["Body"])
    assert body["type"] == "OrcamentoGerado"
    assert response["Attributes"]["MessageGroupId"] == generate["sagaId"]
    assert response["Attributes"]["MessageDeduplicationId"] == body["messageId"]
    assert response["MessageAttributes"] == attrs


@mock_aws
def test_invalid_command_is_not_acknowledged(billing, monkeypatch):
    client = boto3.client("sqs", region_name="us-east-1")
    queue = client.create_queue(QueueName="bad.fifo", Attributes={"FifoQueue": "true"})["QueueUrl"]
    client.send_message(
        QueueUrl=queue, MessageBody="{}", MessageGroupId="g", MessageDeduplicationId="m"
    )
    assert SQSConsumer(client, queue, billing).once() == 0
    attributes = client.get_queue_attributes(
        QueueUrl=queue, AttributeNames=["ApproximateNumberOfMessagesNotVisible"]
    )["Attributes"]
    assert attributes["ApproximateNumberOfMessagesNotVisible"] == "1"


def test_queue_settings_required():
    with pytest.raises(ValueError):
        SQSConsumer(None, "", None)
    with pytest.raises(ValueError):
        SQSPublisher(None, "")


def test_trace_survives_approval_and_payment(billing, db, generate):
    from billing_service.domain import Observation
    from tests.conftest import message

    attrs = trace_attributes({"traceparent": TRACE, "tracestate": "vendor=value"})
    qid = generated(billing, generate, attrs)
    billing.decide(qid, 7, True)
    billing.handle(
        message("SolicitarPagamento", {"orcamentoId": qid, "valorTotalCentavos": 20000}, generate),
        attrs,
    )
    pid = billing.payment(qid, 7)["pagamentoId"]
    billing.observe(pid, Observation("p1", pid, 20000, "BRL", "approved"))
    sent = []

    class Publisher:
        def publish(self, m, a):
            sent.append(a)

    while relay_once(db, Publisher()):
        pass
    assert sent == [attrs, attrs, attrs]


class FakeAgent:
    def __init__(self):
        self.events = []

    def application(self):
        return "app"

    def BackgroundTask(self, app, name, group):  # noqa: N802 - mirrors the agent API
        agent = self

        class Task:
            def __enter__(self):
                agent.events.append(("enter", app, name, group))

            def __exit__(self, *exc):
                agent.events.append(("exit",))

        return Task()

    def accept_distributed_trace_headers(self, headers, transport_type):
        self.events.append(("accept", dict(headers), transport_type))


class SpyClient:
    def __init__(self, message):
        self.message, self.deleted = message, []

    def receive_message(self, **kwargs):
        return {"Messages": [self.message]}

    def delete_message(self, **kwargs):
        self.deleted.append(kwargs)


def _message(body, attributes):
    return {"Body": json.dumps(body), "ReceiptHandle": "r", "MessageAttributes": attributes}


def test_consumer_runs_inside_agent_transaction_with_incoming_trace(monkeypatch):
    import sys
    import types

    fake = FakeAgent()
    handled = []

    class Billing:
        def handle(self, body, attrs):
            fake.events.append(("handle",))
            handled.append(attrs)

    module = types.ModuleType("newrelic")
    module.agent = fake
    monkeypatch.setitem(sys.modules, "newrelic", module)
    monkeypatch.setitem(sys.modules, "newrelic.agent", fake)
    attrs = trace_attributes({"traceparent": TRACE, "tracestate": "v=1"})
    client = SpyClient(_message({"type": "GerarOrcamento"}, attrs))
    assert SQSConsumer(client, "q", Billing()).once() == 1
    assert fake.events == [
        ("enter", "app", "GerarOrcamento", "Message/SQS"),
        ("accept", {"traceparent": TRACE, "tracestate": "v=1"}, "Queue"),
        ("handle",),
        ("exit",),
    ]
    assert handled == [attrs]


def test_consumer_without_agent_is_unchanged(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "newrelic", None)
    monkeypatch.setitem(sys.modules, "newrelic.agent", None)
    seen = []

    class Billing:
        def handle(self, body, attrs):
            seen.append(attrs)

    attrs = trace_attributes({"traceparent": TRACE})
    client = SpyClient(_message({"type": "X"}, attrs))
    assert SQSConsumer(client, "q", Billing()).once() == 1
    assert seen == [attrs] and len(client.deleted) == 1
