# def evaluate_condition(
#     situation,
#     condition: dict,
# ) -> bool:
#     if not condition:
#         return True

#     for field, expected_value in condition.items():
#         actual_value = getattr(
#             situation,
#             field,
#             None,
#         )

#         if isinstance(
#             expected_value,
#             list,
#         ):
#             if actual_value not in expected_value:
#                 return False
#         else:
#             if actual_value != expected_value:
#                 return False

#     return True


def _situation_alerts(situation):
    return list(getattr(situation, "alerts", []) or [])


def _matches_alert_field(situation, field: str, expected_value) -> bool:
    alerts = _situation_alerts(situation)

    if field in {"source", "policy_name", "service", "environment"}:
        situation_value = getattr(situation, field, None)
        if situation_value is not None and situation_value == expected_value:
            return True

        return any(
            getattr(alert, field, None) == expected_value
            for alert in alerts
        )

    return False


def _matches_tag(situation, expected_value: str) -> bool:
    expected = expected_value.strip().lower()
    if not expected:
        return True

    for alert in _situation_alerts(situation):
        raw_tags = getattr(alert, "tags", None) or ""
        tags = {tag.strip().lower() for tag in raw_tags.split(",") if tag.strip()}
        if expected in tags:
            return True

    return False


def evaluate_condition(situation, condition: dict) -> bool:
    if not condition:
        return True

    for field, expected_value in condition.items():
        if field == "tag":
            if not isinstance(expected_value, str) or not _matches_tag(
                situation, expected_value
            ):
                return False
            continue

        if field in {"source", "policy_name", "service", "environment"} and not isinstance(
            expected_value, list
        ):
            if not _matches_alert_field(
                situation, field, expected_value
            ):
                return False
            continue

        actual_value = getattr(
            situation,
            field,
            None,
        )

        if isinstance(expected_value, list):
            if actual_value not in expected_value:
                return False
        else:
            if actual_value != expected_value:
                return False

    return True
