from app.correlation.rules import (
    overlapping_tags,
    same_environment,
    same_policy,
    same_service,
    within_time_window,
)


class CorrelationEngine:
    def get_reasons(self, alert_1, alert_2) -> list[str]:
        reasons = []

        if same_service(alert_1, alert_2):
            reasons.append("Same service")

        if same_environment(alert_1, alert_2):
            reasons.append("Same environment")

        if same_policy(alert_1, alert_2):
            reasons.append("Same policy")

        if overlapping_tags(alert_1, alert_2):
            reasons.append("Overlapping tags")

        if within_time_window(alert_1, alert_2):
            reasons.append("Within correlation time window")

        return reasons

    def calculate_score(self, alert_1, alert_2) -> int:
        score = 0

        if same_service(alert_1, alert_2):
            score += 40

        if same_environment(alert_1, alert_2):
            score += 25

        if same_policy(alert_1, alert_2):
            score += 20

        if overlapping_tags(alert_1, alert_2):
            score += 10

        if within_time_window(alert_1, alert_2):
            score += 5

        return score

    def are_related(
        self,
        alert_1,
        alert_2,
        threshold: int = 60,
    ) -> bool:
        return (
            self.calculate_score(alert_1, alert_2)
            >= threshold
        )


    def calculate_situation_severity(
        self,
        alerts,
    ) -> str:
        severity_priority = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }

        highest_severity = "Low"
        highest_score = 0

        for alert in alerts:
            severity = (
                alert.severity or "Medium"
            ).lower()

            score = severity_priority.get(
                severity,
                2,
            )

            if score > highest_score:
                highest_score = score
                highest_severity = (
                    alert.severity
                    or "Medium"
                )

        return highest_severity

    def calculate_hybrid_score(
        self,
        rule_score: int,
        historical_score: float,
    ) -> float:
        return (
            (rule_score * 0.8)
            + (historical_score * 0.2)
        )