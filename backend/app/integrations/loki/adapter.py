from app.alerts.schema import AlertCreate


class LokiAdapter:
    @staticmethod
    def normalize_log(data: dict) -> AlertCreate:
        labels = data.get("labels", {})
        message = data.get("message", "Loki log event")

        service = labels.get("service", "unknown")
        level = labels.get("level", "ERROR")

        tags = ",".join(
            f"{key}:{value}"
            for key, value in labels.items()
        )

        return AlertCreate(
            title=f"{level} log from {service}",
            description=message,
            source="Loki",
            severity="Medium",
            policy_name=None,
            tags=tags or None,
        )