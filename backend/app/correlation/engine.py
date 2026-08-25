from app.correlation.rules import (
    same_environment,
    same_policy,
    same_service,
    overlapping_tags,
    within_time_window,
)


class CorrelationEngine:
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
        score = self.calculate_score(
            alert_1,
            alert_2,
        )

        return score >= threshold