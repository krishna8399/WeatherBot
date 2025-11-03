# Monitoring & Metrics (WeatherBot)

Suggested lightweight monitoring:

- Instrument custom actions to log:
  - NLU confidence scores per message
  - Fallback counts and reasons
  - External API latency and HTTP status codes
  - Action execution errors

- Export Prometheus metrics from the actions process using `prometheus_client`.
  Example metrics:
  - weatherapi_requests_total{status="200"}
  - weatherapi_requests_latency_seconds
  - rasa_fallbacks_total

- Create simple Grafana alerts:
  - fallback rate > 5% (warning)
  - API error rate > 2% (critical)
  - average latency > 1s (warning)

Logs: write structured JSON logs to `logs/actions.log` for later analysis.
