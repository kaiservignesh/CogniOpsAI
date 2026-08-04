from app.alerts.service import create_alert
from app.integrations.loki.adapter import LokiAdapter
from app.integrations.loki.client import LokiClient
from sqlalchemy.orm import Session


class LokiService:
    def __init__(self):
        self.client = LokiClient()

    def ingest_logs(
        self,
        db: Session,
        query: str,
        limit: int = 100,
    ):
        data = self.client.query_logs(
            query=query,
            limit=limit,
        )

        results = data.get("data", {}).get(
            "result", []
        )

        created_alerts = []

        for stream in results:
            labels = stream.get("stream", {})

            for entry in stream.get("values", []):
                timestamp, message = entry

                log_data = {
                    "labels": labels,
                    "message": message,
                    "timestamp": timestamp,
                }

                alert_data = LokiAdapter.normalize_log(
                    log_data
                )

                alert = create_alert(
                    db,
                    alert_data,
                )

                created_alerts.append(alert)

        return created_alerts