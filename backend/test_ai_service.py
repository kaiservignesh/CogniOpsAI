from app.ai.service import AIService


sample_context = {
    "id": 1,
    "title": "Payment API Production Incident",
    "description": (
        "Multiple monitoring signals indicate "
        "a possible payment service issue."
    ),
    "severity": "Critical",
    "status": "Open",
    "service": "payment-api",
    "environment": "production",
    "alert_count": 3,
    "alerts": [
        {
            "id": 101,
            "title": "CPU usage exceeded 95%",
            "source": "New Relic",
            "severity": "Critical",
            "service": "payment-api",
            "environment": "production",
            "policy_name": "Production CPU Policy",
            "tags": "payment-api,production",
        },
        {
            "id": 102,
            "title": "High CPU Usage",
            "source": "Grafana",
            "severity": "High",
            "service": "payment-api",
            "environment": "production",
            "policy_name": "High CPU Rule",
            "tags": "payment-api,production",
        },
        {
            "id": 103,
            "title": "Database connection timeout",
            "source": "Loki",
            "severity": "Medium",
            "service": "payment-api",
            "environment": "production",
            "policy_name": None,
            "tags": "payment-api,production",
        },
    ],
}


def main():
    service = AIService()

    summary = service.summarize_situation(
        sample_context
    )

    print("\nAI Situation Summary:\n")
    print(summary)


if __name__ == "__main__":
    main()