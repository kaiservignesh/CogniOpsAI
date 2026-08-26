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

        return [
            candidate
            for candidate in alerts
            if self.engine.are_related(
                alert,
                candidate,
            )
        ]

    def find_existing_situation(
        self,
        db: Session,
        alert: Alert,
    ):
        situations = (
            db.query(Situation)
            .filter(
                Situation.status.in_(
                    ["Open", "Investigating"]
                )
            )
            .all()
        )

        best_match = None
        best_score = 0
        best_reasons = []

        for situation in situations:
            situation_alerts = (
                db.query(Alert)
                .filter(
                    Alert.situation_id
                    == situation.id
                )
                .all()
            )

            for existing_alert in situation_alerts:
                score = self.engine.calculate_score(
                    alert,
                    existing_alert,
                )

                if score > best_score:
                    best_score = score
                    best_match = situation
                    best_reasons = (
                        self.engine.get_reasons(
                            alert,
                            existing_alert,
                        )
                    )

        if best_score < 60:
            return None

        return {
            "situation": best_match,
            "score": best_score,
            "reasons": best_reasons,
        }

    def attach_to_situation(
        self,
        db: Session,
        alert: Alert,
        situation: Situation,
    ):
        alert.situation_id = situation.id

        db.commit()
        db.refresh(alert)

        return self.update_situation_severity(
            db,
            situation,
        )

    def create_situation_from_alerts(
        self,
        db: Session,
        alert: Alert,
        related_alerts: list[Alert],
    ) -> Situation:
        all_alerts = [
            alert,
            *related_alerts,
        ]

        situation = Situation(
            title=f"Correlated incident: {alert.title}",
            description=(
                f"Situation created from alert "
                f"{alert.id} and "
                f"{len(related_alerts)} "
                f"related alert(s)."
            ),
            severity=(
                self.engine.calculate_situation_severity(
                    all_alerts
                )
            ),
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
    ):
        alert = (
            db.query(Alert)
            .filter(Alert.id == alert_id)
            .first()
        )

        if alert is None:
            return None

        # Already correlated
        if alert.situation_id is not None:
            situation = (
                db.query(Situation)
                .filter(
                    Situation.id
                    == alert.situation_id
                )
                .first()
            )

            return {
                "situation": situation,
                "score": 100,
                "reasons": [
                    "Alert already belongs "
                    "to this situation"
                ],
            }

        # First try existing situations
        existing = self.find_existing_situation(
            db,
            alert,
        )

        if existing is not None:
            situation = self.attach_to_situation(
                db,
                alert,
                existing["situation"],
            )

            return {
                "situation": situation,
                "score": existing["score"],
                "reasons": existing["reasons"],
            }

        # Otherwise try unassigned alerts
        related_alerts = self.find_related_alerts(
            db,
            alert,
        )

        if not related_alerts:
            return None

        situation = (
            self.create_situation_from_alerts(
                db,
                alert,
                related_alerts,
            )
        )

        return {
            "situation": situation,
            "score": max(
                self.engine.calculate_score(
                    alert,
                    related_alerts[0],
                ),
                60,
            ),
            "reasons": self.engine.get_reasons(
                alert,
                related_alerts[0],
            ),
        }

    def update_situation_severity(
        self,
        db: Session,
        situation: Situation,
    ):
        alerts = (
            db.query(Alert)
            .filter(
                Alert.situation_id
                == situation.id
            )
            .all()
        )

        if not alerts:
            return situation

        situation.severity = (
            self.engine.calculate_situation_severity(
                alerts
            )
        )

        db.commit()
        db.refresh(situation)

        return situation