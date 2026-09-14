from datetime import datetime


CORRELATION_TIME_WINDOW_MINUTES = 5


def same_service(alert_1, alert_2) -> bool:
    if not alert_1.service or not alert_2.service:
        return False

    return alert_1.service == alert_2.service


def same_environment(alert_1, alert_2) -> bool:
    if not alert_1.environment or not alert_2.environment:
        return False

    return alert_1.environment == alert_2.environment


def same_policy(alert_1, alert_2) -> bool:
    if not alert_1.policy_name or not alert_2.policy_name:
        return False

    return alert_1.policy_name == alert_2.policy_name


def same_issue(alert_1, alert_2) -> bool:
    if not alert_1.tags or not alert_2.tags:
        return False

    tags_1 = {
        tag.strip().lower()
        for tag in alert_1.tags.split(",")
        if tag.strip().lower().startswith("issue:")
    }

    tags_2 = {
        tag.strip().lower()
        for tag in alert_2.tags.split(",")
        if tag.strip().lower().startswith("issue:")
    }

    return bool(tags_1.intersection(tags_2))


def overlapping_tags(alert_1, alert_2) -> bool:
    if not alert_1.tags or not alert_2.tags:
        return False

    tags_1 = {
        tag.strip().lower()
        for tag in alert_1.tags.split(",")
        if tag.strip()
    }

    tags_2 = {
        tag.strip().lower()
        for tag in alert_2.tags.split(",")
        if tag.strip()
    }

    return bool(tags_1.intersection(tags_2))


def within_time_window(alert_1, alert_2) -> bool:
    if not alert_1.created_at or not alert_2.created_at:
        return False

    difference = abs(
        (
            alert_1.created_at
            - alert_2.created_at
        ).total_seconds()
    )

    return (
        difference
        <= CORRELATION_TIME_WINDOW_MINUTES * 60
    )


def should_correlate(alert_1, alert_2) -> bool:
    """
    Determine whether two alerts are likely related.

    Service and environment provide context, but they are not
    sufficient by themselves to merge unrelated alert types.
    """

    if not within_time_window(alert_1, alert_2):
        return False

    if same_issue(alert_1, alert_2):
        return True

    if same_policy(alert_1, alert_2) and same_service(
        alert_1, alert_2
    ):
        return True

    if same_policy(alert_1, alert_2) and same_environment(
        alert_1, alert_2
    ):
        return True

    return False
