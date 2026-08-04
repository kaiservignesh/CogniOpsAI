from app.alerts.service import create_alert
from app.integrations.newrelic.adapter import NewRelicAdapter
from app.integrations.newrelic.client import NewRelicClient
from sqlalchemy.orm import Session


class NewRelicService:
    def __init__(self):
        self.client = NewRelicClient()

    def ingest_alerts(self, db: Session):
        data = self.client.get_alerts()

        violations = data.get("violations", [])

        created_alerts = []

        for violation in violations:
            alert_data = NewRelicAdapter.normalize_alert(
                {"violation": violation}
            )

            alert = create_alert(db, alert_data)
            created_alerts.append(alert)

        return created_alerts