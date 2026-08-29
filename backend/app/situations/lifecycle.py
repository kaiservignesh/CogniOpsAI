ALLOWED_TRANSITIONS = {
    "Open": {
        "Investigating",
        "Resolved",
    },
    "Investigating": {
        "Resolved",
    },
    "Resolved": set(),
}


def validate_status_transition(
    current_status: str,
    new_status: str,
) -> bool:
    if current_status == new_status:
        return True

    allowed = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    return new_status in allowed