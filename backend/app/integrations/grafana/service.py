from app.alerts.service import create_alert
from app.integrations.grafana.adapter import GrafanaAdapter
from app.integrations.grafana.client import GrafanaClient
from sqlalchemy.orm import Session


class GrafanaService:
    def __init__(self):
        self.client = GrafanaClient()

    def ingest_alerts(self, db: Session):
        data = self.client.get_alerts()

        if not isinstance(data, list):
            raise ValueError("Unexpected Grafana alert response")

        created_alerts = []

        for item in data:
            alert_data = GrafanaAdapter.normalize_alert(item)

            alert = create_alert(db, alert_data)
            created_alerts.append(alert)

        return created_alerts