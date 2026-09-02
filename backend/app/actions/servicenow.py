import uuid

from app.actions.base import ActionAdapter


class ServiceNowActionAdapter(ActionAdapter):
    def execute(
        self,
        payload: dict,
    ) -> str:
        title = payload.get(
            "title",
            "CogniOpsAI Incident",
        )

        description = payload.get(
            "description",
            "Incident created by CogniOpsAI.",
        )

        severity = payload.get(
            "severity",
            "High",
        )

        service = payload.get(
            "service",
            "Unknown",
        )

        environment = payload.get(
            "environment",
            "Unknown",
        )

        incident_number = (
            f"INC{uuid.uuid4().hex[:8].upper()}"
        )

        return (
            "Mock ServiceNow incident created successfully. "
            f"Incident: {incident_number}; "
            f"Title: {title}; "
            f"Severity: {severity}; "
            f"Service: {service}; "
            f"Environment: {environment}; "
            f"Description: {description}"
        )