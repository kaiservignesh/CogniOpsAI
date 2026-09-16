from app.alerts.schema import AlertCreate

def normalize_status(value: str | None) -> str:
    if not value:
        return "Open"

    normalized = value.strip().lower()

    status_map = {
        "open": "Open",
        "opened": "Open",
        "firing": "Open",
        "triggered": "Open",
        "acknowledged": "Investigating",
        "investigating": "Investigating",
        "closed": "Resolved",
        "resolved": "Resolved",
    }

    return status_map.get(
        normalized,
        value.strip().title(),
    )

def normalize_severity(value: str | None) -> str:
    if not value:
        return "Medium"

    normalized = value.strip().lower()

    severity_map = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "warning": "Medium",
        "low": "Low",
        "info": "Low",
        "informational": "Low",
    }

    return severity_map.get(
        normalized,
        value.strip().title(),
    )
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

        service = violation.get(
            "service",
            "N/A",
        )

        environment = violation.get(
            "environment",
            "N/A",
        )

        policy_name = violation.get("policy_name")

        entity_name = violation.get(
            "entity",
            "unknown",
        )

        return AlertCreate(
            title=title,
            description=description,
            source="New Relic",
            severity=severity,
            service=service,
            environment=environment,
            policy_name=policy_name,
            tags=f"entity:{entity_name}",
        )

    @staticmethod
    def normalize_webhook(data: dict) -> AlertCreate:
        """
        Normalize a New Relic webhook payload.

        Supports the fields we expect to send from a
        New Relic workflow while providing safe defaults
        for missing fields.
        """

        title = (
            data.get("title")
            or data.get("issue_title")
            or data.get("name")
            or "New Relic Alert"
        )

        description = (
            data.get("description")
            or data.get("issue_description")
            or "Alert received from New Relic"
        )

        status = normalize_status(
            data.get("status")
            or data.get("state")
            or data.get("issue_state")
        )

        severity = normalize_severity(
            data.get("priority")
            or data.get("severity")                                                            
            or "Medium"
        )

        service = (
            data.get("service")
            or data.get("application")
            or "N/A"
        )

        environment = (
            data.get("environment")
            or data.get("environment_name")
            or "N/A"
        )

        policy_name = (
            data.get("policy_name")
            or data.get("condition_name")
            or data.get("conditionName")
        )

        entity = (
            data.get("entity")
            or data.get("entity_name")
            or "unknown"
        )

        issue_id = data.get("issue_id") or data.get("issueId")

        tags = [
            f"entity:{entity}",
        ]

        # raw_tags = data.get("tags", {})
        
        # if isinstance(raw_tags, dict):
        #     tags = [
        #         f"{key}:{value}"
        #         for key, value in raw_tags.items()
        #         if value
        #     ]
        # else:
        #     tags = []

        if entity:
            tags.append(f"entity:{entity}")

        if issue_id:
            tags.append(f"issue:{issue_id}")

        return AlertCreate(
            title=title,
            description=description,
            source="New Relic",
            severity=severity,
            status=status,
            service=service,
            environment=environment,
            policy_name=policy_name,
            tags=",".join(tags) or None,
        )

    