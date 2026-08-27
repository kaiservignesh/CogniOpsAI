def build_situation_summary_prompt(
    situation_context: dict,
) -> str:
    alerts = situation_context.get("alerts", [])

    alert_details = "\n".join(
        [
            (
                f"- Alert ID: {alert['id']}\n"
                f"  Title: {alert['title']}\n"
                f"  Source: {alert['source']}\n"
                f"  Severity: {alert['severity']}\n"
                f"  Service: {alert.get('service')}\n"
                f"  Environment: "
                f"{alert.get('environment')}\n"
                f"  Policy: "
                f"{alert.get('policy_name')}\n"
                f"  Tags: {alert.get('tags')}"
            )
            for alert in alerts
        ]
    )

    return f"""
You are an AIOps incident analysis assistant.

Analyze the following operational situation.

Situation:
Title: {situation_context.get("title")}
Description: {situation_context.get("description")}
Severity: {situation_context.get("severity")}
Status: {situation_context.get("status")}
Service: {situation_context.get("service")}
Environment: {situation_context.get("environment")}
Alert Count: {situation_context.get("alert_count")}

Related Alerts:
{alert_details}

Provide a concise incident summary in 3-5 sentences.

Focus on:
1. What is happening.
2. Which service or environment is affected.
3. The most important observable symptoms.
4. Why the alerts appear related.

Do not invent facts that are not present in the provided information.
"""

def build_root_cause_prompt(
    situation_context: dict,
    historical_context: str = "",
) -> str:
    alerts = situation_context.get("alerts", [])

    alert_details = "\n".join(
        [
            (
                f"- Alert ID: {alert['id']}\n"
                f"  Title: {alert['title']}\n"
                f"  Source: {alert['source']}\n"
                f"  Severity: {alert['severity']}\n"
                f"  Service: {alert.get('service')}\n"
                f"  Environment: "
                f"{alert.get('environment')}\n"
                f"  Policy: "
                f"{alert.get('policy_name')}\n"
                f"  Tags: {alert.get('tags')}"
            )
            for alert in alerts
        ]
    )

    return f"""
You are an AIOps root-cause analysis assistant.

Analyze the current operational situation using the
current alert evidence and any relevant historical context.

Current Situation:
Title: {situation_context.get("title")}
Description: {situation_context.get("description")}
Severity: {situation_context.get("severity")}
Status: {situation_context.get("status")}
Service: {situation_context.get("service")}
Environment: {situation_context.get("environment")}
Alert Count: {situation_context.get("alert_count")}

Current Alerts:
{alert_details}

Historical Similar Situations:
{historical_context or "No historical context available."}

Provide the response using exactly this structure:

Probable Root Cause:
<one concise statement>

Confidence:
<Low, Medium, or High>

Evidence:
- <current evidence>
- <current evidence>
- <historical evidence if relevant>

Historical Comparison:
<briefly explain whether a similar historical situation
supports the root-cause hypothesis>

Important rules:
- Do not invent facts.
- Do not claim a root cause is certain.
- Distinguish observed symptoms from inferred causes.
- Treat historical situations as supporting evidence, not proof.
- If evidence is insufficient, say so clearly.
"""

def build_recommendation_prompt(
    situation_context: dict,
    historical_context: str = "",
) -> str:
    alerts = situation_context.get("alerts", [])

    alert_details = "\n".join(
        [
            (
                f"- Alert ID: {alert['id']}\n"
                f"  Title: {alert['title']}\n"
                f"  Source: {alert['source']}\n"
                f"  Severity: {alert['severity']}\n"
                f"  Service: {alert.get('service')}\n"
                f"  Environment: "
                f"{alert.get('environment')}\n"
                f"  Policy: "
                f"{alert.get('policy_name')}\n"
                f"  Tags: {alert.get('tags')}"
            )
            for alert in alerts
        ]
    )

    return f"""
You are an AIOps incident-response assistant.

Recommend practical next actions for the current operational
situation using the current evidence and relevant historical
situations.

Current Situation:
Title: {situation_context.get("title")}
Description: {situation_context.get("description")}
Severity: {situation_context.get("severity")}
Status: {situation_context.get("status")}
Service: {situation_context.get("service")}
Environment: {situation_context.get("environment")}
Alert Count: {situation_context.get("alert_count")}

Current Alerts:
{alert_details}

Historical Similar Situations:
{historical_context or "No historical context available."}

Provide exactly this structure:

Recommended Actions:
1. <action>
2. <action>
3. <action>

Priority:
<High, Medium, or Low>

Reason:
<brief explanation>

Historical Guidance:
<explain whether a previous similar situation provides useful
guidance for the recommended actions>

Important rules:
- Do not invent infrastructure details.
- Do not claim an action is guaranteed to solve the issue.
- Prefer investigation and verification before destructive actions.
- Do not recommend deleting data or permanently changing
  production systems.
- Treat historical situations as guidance, not proof.
- Base recommendations only on the supplied evidence.
"""

