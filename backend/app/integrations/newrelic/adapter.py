from app.alerts.schema import AlertCreate


class NewRelicAdapter:
    @staticmethod
    def normalize_alert(data: dict) -> AlertCreate:
        violation = data.get("violation", {})

        title = violation.get(
            "description",
            "New Relic Alert",
        )

        description = violation.get(
            "description",
            "Alert received from New Relic",
        )

        severity = violation.get(
            "priority",
            "Medium",
        )

        policy_name = violation.get(
            "policy_name"
        )

        entity_name = violation.get(
            "entity",
            "unknown",
        )

        return AlertCreate(
            title=title,
            description=description,
            source="New Relic",
            severity=severity,
            policy_name=policy_name,
            tags=f"entity:{entity_name}",
        )