#!/bin/sh
# Roda o comando sob o agente New Relic quando ha licenca; sem licenca, direto.
set -e
if [ -n "${NEW_RELIC_LICENSE_KEY:-}" ]; then
  exec newrelic-admin run-program "$@"
fi
exec "$@"
