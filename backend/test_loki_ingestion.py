from unittest.mock import patch

from app.database.database import SessionLocal
from app.integrations.loki.service import LokiService

mock_response = {
    "status": "success",
    "data": {
        "resultType": "streams",
        "result": [
            {
                "stream": {
                    "service": "payment-api",
                    "environment": "production",
                    "level": "ERROR",
                },
                "values": [
                    [
                        "1754043300000000000",
                        "Database connection timeout",
                    ],
                    [
                        "1754043360000000000",
                        "Connection pool exhausted",
                    ],
                ],
            }
        ],
    },
}


def main():
    db = SessionLocal()

    try:
        with patch(
            "app.integrations.loki.client.LokiClient.query_logs",
            return_value=mock_response,
        ):
            service = LokiService()

            alerts = service.ingest_logs(
                db=db,
                query='{service="payment-api"} |= "error"',
            )

            for alert in alerts:
                print(
                    f"Created alert: "
                    f"{alert.id} - {alert.title}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()