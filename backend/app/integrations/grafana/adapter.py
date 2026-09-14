from app.alerts.schema import AlertCreate


class GrafanaAdapter:
    @staticmethod
    def normalize_alert(data: dict) -> AlertCreate:
        title = data.get("title", data.get("name", "Grafana Alert"))
        description = data.get(
            "description",
            "Alert received from Grafana",
        )
        severity = data.get("severity", "Medium")
        policy_name = data.get("rule", data.get("name"))

        labels = data.get("labels", {})
        tags = ",".join(
            f"{key}:{value}"
            for key, value in labels.items()
        )

        return AlertCreate(
            title=title,
            description=description,
            source="Grafana",
            severity=severity,
            policy_name=policy_name,
            tags=tags or None,
        )

    @staticmethod
    def normalize_webhook_alert(data: dict) -> AlertCreate:
        title = (
            data.get("title")
            or data.get("issue_id")
            or "Grafana Alert"
        )

        description = (
            data.get("description")
            or f"Grafana alert: {title}"
        )

        severity = (
            data.get("priority")
            or data.get("severity")
            or "Medium"
        )

        policy_name = (
            data.get("policy_name")
            or data.get("rule")
            or data.get("issue_id")
            or title
        )

        raw_tags = data.get("tags", {})

        if isinstance(raw_tags, dict):
            tag_items = [
                f"{key}:{value}"
                for key, value in raw_tags.items()
                if value
            ]
        else:
            tag_items = []

        issue_id = data.get("issue_id")
        if issue_id:
            tag_items.append(f"issue:{issue_id}")

        entity = data.get("entity")
        if entity:
            tag_items.append(f"entity:{entity}")

        tags = ",".join(tag_items)

        return AlertCreate(
            title=title,
            description=description,
            source="Grafana",
            severity=severity,
            policy_name=policy_name,
            tags=tags or None,
        )