from app.integrations.newrelic.adapter import NewRelicAdapter


sample_payload = {
    "violation": {
        "description": "CPU usage exceeded 95%",
        "priority": "Critical",
        "policy_name": "Production CPU Policy",
        "entity": "payment-service",
    }
}


alert = NewRelicAdapter.normalize_alert(sample_payload)

print(alert.model_dump())