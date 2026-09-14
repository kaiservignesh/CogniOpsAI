from datetime import datetime


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "N/A"

    return value.strftime("%Y-%m-%d %H:%M:%S")


def _append_value(
    lines: list[str],
    label: str,
    value,
):
    if value is None or value == "":
        value = "N/A"

    lines.append(f"{label}: {value}")


def build_situation_email(
    situation,
    execution=None,
    custom_message: str | None = None,
) -> str:
    """
    Build a complete incident email containing:

    - Situation details
    - Correlation details
    - AI analysis
    - All alerts belonging to the situation
    - Workflow execution details
    - Optional custom workflow message
    """

    alerts = list(
        getattr(situation, "alerts", []) or []
    )

    lines: list[str] = []

    # =========================================================
    # Header
    # =========================================================

    lines.append("COGNIOPSAI INCIDENT NOTIFICATION")
    lines.append("=" * 60)
    lines.append("")

    # =========================================================
    # Situation
    # =========================================================

    lines.append("SITUATION")
    lines.append("-" * 60)

    _append_value(
        lines,
        "Situation ID",
        situation.id,
    )

    _append_value(
        lines,
        "Title",
        situation.title,
    )

    _append_value(
        lines,
        "Description",
        situation.description,
    )

    _append_value(
        lines,
        "Severity",
        situation.severity,
    )

    _append_value(
        lines,
        "Status",
        situation.status,
    )

    _append_value(
        lines,
        "Service",
        situation.service,
    )

    _append_value(
        lines,
        "Environment",
        situation.environment,
    )

    _append_value(
        lines,
        "Correlation Score",
        situation.correlation_score,
    )

    _append_value(
        lines,
        "Correlation Method",
        situation.correlation_method,
    )

    _append_value(
        lines,
        "Created At",
        _format_datetime(
            situation.created_at
        ),
    )

    _append_value(
        lines,
        "Updated At",
        _format_datetime(
            situation.updated_at
        ),
    )

    # =========================================================
    # Correlation reasons
    # =========================================================

    lines.append("")
    lines.append("CORRELATION")
    lines.append("-" * 60)

    correlation_reasons = getattr(
        situation,
        "correlation_reasons",
        None,
    )

    if correlation_reasons:
        if isinstance(
            correlation_reasons,
            list,
        ):
            for reason in correlation_reasons:
                lines.append(
                    f"- {reason}"
                )
        else:
            lines.append(
                str(correlation_reasons)
            )
    else:
        lines.append("No correlation reasons available.")

    # =========================================================
    # AI analysis
    # =========================================================

    lines.append("")
    lines.append("AI ANALYSIS")
    lines.append("-" * 60)

    ai_status = getattr(
        situation,
        "ai_status",
        None,
    )

    _append_value(
        lines,
        "AI Status",
        ai_status,
    )

    _append_value(
        lines,
        "AI Updated At",
        _format_datetime(
            getattr(
                situation,
                "ai_updated_at",
                None,
            )
        ),
    )

    lines.append("")
    lines.append("Summary:")
    lines.append(
        getattr(
            situation,
            "ai_summary",
            None,
        )
        or "N/A"
    )

    lines.append("")
    lines.append("Root Cause:")
    lines.append(
        getattr(
            situation,
            "ai_root_cause",
            None,
        )
        or "N/A"
    )

    lines.append("")
    lines.append("Recommendation:")
    lines.append(
        getattr(
            situation,
            "ai_recommendations",
            None,
        )
        or "N/A"
    )

    # =========================================================
    # Alerts
    # =========================================================

    lines.append("")
    lines.append(
        f"ALERTS ({len(alerts)})"
    )
    lines.append("-" * 60)

    if not alerts:
        lines.append(
            "No alerts associated with this situation."
        )
    else:
        for index, alert in enumerate(
            alerts,
            start=1,
        ):
            lines.append("")
            lines.append(
                f"Alert {index}"
            )
            lines.append("." * 30)

            _append_value(
                lines,
                "ID",
                alert.id,
            )

            _append_value(
                lines,
                "Title",
                alert.title,
            )

            _append_value(
                lines,
                "Description",
                alert.description,
            )

            _append_value(
                lines,
                "Source",
                alert.source,
            )

            _append_value(
                lines,
                "Severity",
                alert.severity,
            )

            _append_value(
                lines,
                "Status",
                alert.status,
            )

            _append_value(
                lines,
                "Policy",
                alert.policy_name,
            )

            _append_value(
                lines,
                "Tags",
                alert.tags,
            )

            _append_value(
                lines,
                "Service",
                alert.service,
            )

            _append_value(
                lines,
                "Environment",
                alert.environment,
            )

            _append_value(
                lines,
                "Created At",
                _format_datetime(
                    alert.created_at
                ),
            )

            _append_value(
                lines,
                "Updated At",
                _format_datetime(
                    alert.updated_at
                ),
            )

    # =========================================================
    # Workflow execution
    # =========================================================

    if execution is not None:
        lines.append("")
        lines.append("WORKFLOW EXECUTION")
        lines.append("-" * 60)

        _append_value(
            lines,
            "Execution ID",
            execution.id,
        )

        _append_value(
            lines,
            "Policy ID",
            execution.policy_id,
        )

        _append_value(
            lines,
            "Status",
            execution.status,
        )

        _append_value(
            lines,
            "Action Type",
            execution.action_type,
        )

        _append_value(
            lines,
            "Action Target",
            execution.action_target,
        )

    # =========================================================
    # Custom workflow message
    # =========================================================

    if custom_message:
        lines.append("")
        lines.append("WORKFLOW MESSAGE")
        lines.append("-" * 60)
        lines.append(custom_message)

    # =========================================================
    # Footer
    # =========================================================

    lines.append("")
    lines.append("=" * 60)
    lines.append(
        "Generated automatically by CogniOpsAI."
    )

    return "\n".join(lines)