from unittest.mock import patch

from app.database.database import SessionLocal
from app.integrations.grafana.service import GrafanaService

mock_response = [
    {
        "name": "High CPU Usage",
        "description": "CPU usage exceeded 95%",
        "severity": "Critical",
        "labels": {
            "environment": "production",
            "service": "payment-api",
        },
    },
    {
        "name": "High Memory Usage",
        "description": "Memory usage exceeded 90%",
        "severity": "High",
        "labels": {
            "environment": "production",
            "service": "payment-api",
        },
    },
]


def main():
    db = SessionLocal()

    try:
        with patch(
            "app.integrations.grafana.client.GrafanaClient.get_alerts",
            return_value=mock_response,
        ):
            service = GrafanaService()

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