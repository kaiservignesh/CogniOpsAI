from app.ai.correlation import HistoricalCorrelation
from app.alerts.model import Alert
from app.correlation.engine import CorrelationEngine
from app.models.situation import Situation
from sqlalchemy.orm import Session


class CorrelationService:
    def __init__(self):
        self.engine = CorrelationEngine()
        self.historical = HistoricalCorrelation()

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
        correlation_score: float | None = None,
        correlation_reasons: list[str] | None = None,
        correlation_method: str = "rule + historical",
    ):
        alert.situation_id = situation.id

        if correlation_score is not None:
            situation.correlation_score = correlation_score

        if correlation_reasons is not None:
            situation.correlation_reasons = (
                correlation_reasons
            )

        situation.correlation_method = (
            correlation_method
        )

        db.commit()
        db.refresh(alert)
        db.refresh(situation)

        return self.update_situation_severity(
            db,
            situation,
        )

    def create_situation_from_alerts(
        self,
        db: Session,
        alert: Alert,
        related_alerts: list[Alert],
        correlation_score: float = 0.0,
        correlation_method: str = "rule-based",
        correlation_reasons: list[str] | None = None,
    ) -> Situation:
        all_alerts = [
            alert,
            *related_alerts,
        ]

        situation = Situation(
            title=(
                f"Correlated incident: "
                f"{alert.title}"
            ),
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
            correlation_score=correlation_score,
            correlation_method=correlation_method,
            correlation_reasons=(
                correlation_reasons or []
            ),
        )

        db.add(situation)
        db.flush()

        alert.situation_id = situation.id

        for related_alert in related_alerts:
            related_alert.situation_id = (
                situation.id
            )

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

        # Alert is already associated with a situation.
        if alert.situation_id is not None:
            situation = (
                db.query(Situation)
                .filter(
                    Situation.id
                    == alert.situation_id
                )
                .first()
            )

            if situation is None:
                return None

            return {
                "situation": situation,
                "score": 100,
                "reasons": [
                    "Alert already belongs ",
                    "to this situation"
                ],
            }

        # First try to match an existing situation.
        existing = self.find_existing_situation(
            db,
            alert,
        )

        if existing is not None:
            situation = self.attach_to_situation(
                db=db,
                alert=alert,
                situation=existing["situation"],
                correlation_score=existing["score"],
                correlation_reasons=existing["reasons"],
                correlation_method="rule-based",
            )

            return {
                "situation": situation,
                "score": existing["score"],
                "reasons": existing["reasons"],
            }

        # Otherwise find related unassigned alerts.
        related_alerts = self.find_related_alerts(
            db,
            alert,
        )

        if not related_alerts:
            return None

        hybrid_result = (
            self.hybrid_correlation_analysis(
                db,
                alert,
                related_alerts,
            )
        )

        situation = (
            self.create_situation_from_alerts(
                db=db,
                alert=alert,
                related_alerts=related_alerts,
                correlation_score=(
                    hybrid_result["hybrid_score"]
                ),
                correlation_method=(
                    "rule + historical"
                ),
                correlation_reasons=(
                    hybrid_result["reasons"]
                ),
            )
        )

        return {
            "situation": situation,
            "score": hybrid_result["hybrid_score"],
            "reasons": hybrid_result["reasons"],
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

    def hybrid_correlation_analysis(
        self,
        db: Session,
        alert: Alert,
        related_alerts: list[Alert] | None = None,
    ):
        if related_alerts is None:
            related_alerts = (
                self.find_related_alerts(
                    db,
                    alert,
                )
            )

        if not related_alerts:
            return {
                "rule_score": 0,
                "historical_score": 0.0,
                "hybrid_score": 0.0,
                "reasons": [],
            }

        best_rule_score = 0
        best_reasons = []

        for candidate in related_alerts:
            score = self.engine.calculate_score(
                alert,
                candidate,
            )

            if score > best_rule_score:
                best_rule_score = score
                best_reasons = (
                    self.engine.get_reasons(
                        alert,
                        candidate,
                    )
                )

        context = {
            "title": alert.title,
            "description": alert.description,
            "service": alert.service,
            "environment": alert.environment,
            "alerts": [
                {
                    "title": alert.title,
                }
            ],
        }

        historical_score = (
            self.historical.calculate_similarity_score(
                context
            )
        )

        hybrid_score = (
            self.engine.calculate_hybrid_score(
                best_rule_score,
                historical_score,
            )
        )

        return {
            "rule_score": best_rule_score,
            "historical_score": round(
                historical_score,
                2,
            ),
            "hybrid_score": round(
                hybrid_score,
                2,
            ),
            "reasons": best_reasons,
        }