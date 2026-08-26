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

Analyze the following operational situation using ONLY
the evidence provided.

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

Provide the response using exactly this structure:

Probable Root Cause:
<one concise statement>

Confidence:
<Low, Medium, or High>

Evidence:
- <evidence point 1>
- <evidence point 2>
- <evidence point 3>

Important rules:
- Do not invent facts.
- Do not claim a root cause is certain.
- Distinguish observed symptoms from inferred causes.
- If the evidence is insufficient, say so clearly.
"""