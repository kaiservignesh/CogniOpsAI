from unittest.mock import patch

from app.database.database import SessionLocal
from app.integrations.newrelic.service import NewRelicService


mock_response = {
    "violations": [
        {
            "description": "CPU usage exceeded 95%",
            "priority": "Critical",
            "policy_name": "Production CPU Policy",
            "entity": "payment-service",
        },
        {
            "description": "Memory usage exceeded 90%",
            "priority": "High",
            "policy_name": "Production Memory Policy",
            "entity": "payment-service",
        },
    ]
}


def main():
    db = SessionLocal()

    try:
        with patch(
            "app.integrations.newrelic.client.NewRelicClient.get_alerts",
            return_value=mock_response,
        ):
            service = NewRelicService()

            alerts = service.ingest_alerts(db)

            for alert in alerts:
                print(
                    f"Created alert: "
                    f"{alert.id} - {alert.title}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()