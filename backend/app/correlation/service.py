from app.alerts.model import Alert
from app.correlation.engine import CorrelationEngine
from app.models.situation import Situation
from sqlalchemy.orm import Session


class CorrelationService:
    def __init__(self):
        self.engine = CorrelationEngine()

    def find_related_alerts(
        self,
        db: Session,
        alert: Alert,
    ) -> list[Alert]:
        alerts = (
            db.query(Alert)
            .filter(
                Alert.id != alert.id,
                Alert.situation_id.is_(None),
            )
            .all()
        )

        related_alerts = []

        for candidate in alerts:
            if self.engine.are_related(
                alert,
                candidate,
            ):
                related_alerts.append(candidate)

        return related_alerts

    def create_situation_from_alerts(
        self,
        db: Session,
        alert: Alert,
        related_alerts: list[Alert],
    ) -> Situation:
        situation = Situation(
            title=f"Correlated incident: {alert.title}",
            description=(
                f"Situation created from alert "
                f"{alert.id} and "
                f"{len(related_alerts)} related alert(s)."
            ),
            severity=alert.severity,
            status="Open",
            service=alert.service,
            environment=alert.environment,
        )

        db.add(situation)
        db.flush()

        alert.situation_id = situation.id

        for related_alert in related_alerts:
            related_alert.situation_id = situation.id

        db.commit()
        db.refresh(situation)

        return situation

    def correlate_alert(
        self,
        db: Session,
        alert_id: int,
    ) -> Situation | None:
        alert = (
            db.query(Alert)
            .filter(Alert.id == alert_id)
            .first()
        )

        if alert is None:
            return None

        if alert.situation_id is not None:
            return (
                db.query(Situation)
                .filter(
                    Situation.id == alert.situation_id
                )
                .first()
            )

        related_alerts = self.find_related_alerts(
            db,
            alert,
        )

        if not related_alerts:
            return None

        return self.create_situation_from_alerts(
            db,
            alert,
            related_alerts,
        )