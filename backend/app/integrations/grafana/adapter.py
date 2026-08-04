from app.alerts.schema import AlertCreate


class GrafanaAdapter:
    @staticmethod
    def normalize_alert(data: dict) -> AlertCreate:
        title = data.get(
            "title",
            data.get("name", "Grafana Alert"),
        )

        description = data.get(
            "description",
            "Alert received from Grafana",
        )

        severity = data.get(
            "severity",
            "Medium",
        )

        policy_name = data.get(
            "rule",
            data.get("name"),
        )

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