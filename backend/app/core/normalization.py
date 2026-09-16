def normalize_alert_status(
    value: str | None,
) -> str:
    if not value:
        return "Open"

    normalized = value.strip().lower()

    if normalized in {
        "open",
        "opened",
        "firing",
        "triggered",
    }:
        return "Open"

    if normalized in {
        "acknowledged",
        "investigating",
    }:
        return "Investigating"

    if normalized in {
        "closed",
        "resolved",
    }:
        return "Resolved"

    return value.strip().title()