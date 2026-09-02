import uuid

from app.actions.base import ActionAdapter


class XMattersActionAdapter(ActionAdapter):
    def execute(
        self,
        payload: dict,
    ) -> str:
        recipient = payload.get(
            "recipient",
            "operations",
        )

        subject = payload.get(
            "subject",
            "CogniOpsAI Incident",
        )

        message = payload.get(
            "message",
            "CogniOpsAI detected an operational incident.",
        )

        notification_id = (
            f"XM-{uuid.uuid4().hex[:8].upper()}"
        )

        return (
            "Mock xMatters notification sent successfully. "
            f"Notification: {notification_id}; "
            f"Recipient: {recipient}; "
            f"Subject: {subject}; "
            f"Message: {message}"
        )