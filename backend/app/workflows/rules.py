def evaluate_condition(
    situation,
    condition: dict,
) -> bool:
    if not condition:
        return True

    for field, expected_value in condition.items():
        actual_value = getattr(
            situation,
            field,
            None,
        )

        if isinstance(
            expected_value,
            list,
        ):
            if actual_value not in expected_value:
                return False
        else:
            if actual_value != expected_value:
                return False

    return True