import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from app.actions.base import ActionAdapter

load_dotenv()


class EmailActionAdapter(ActionAdapter):
    def execute(
        self,
        payload: dict,
    ) -> str:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(
            os.getenv(
                "SMTP_PORT",
                "587",
            )
        )
        smtp_username = os.getenv(
            "SMTP_USERNAME"
        )
        smtp_password = os.getenv(
            "SMTP_PASSWORD"
        )
        smtp_from = os.getenv(
            "SMTP_FROM"
        )

        recipient = payload.get("recipient")
        subject = payload.get(
            "subject",
            "CogniOpsAI Incident Notification",
        )
        body = payload.get(
            "body",
            "CogniOpsAI workflow notification.",
        )

        if not recipient:
            raise ValueError(
                "Email recipient is required"
            )

        if not smtp_host:
            raise ValueError(
                "SMTP_HOST is not configured"
            )

        if not smtp_username:
            raise ValueError(
                "SMTP_USERNAME is not configured"
            )

        if not smtp_password:
            raise ValueError(
                "SMTP_PASSWORD is not configured"
            )

        if not smtp_from:
            raise ValueError(
                "SMTP_FROM is not configured"
            )

        message = EmailMessage()

        message["From"] = smtp_from
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30,
        ) as server:
            server.starttls()
            server.login(
                smtp_username,
                smtp_password,
            )
            server.send_message(message)

        return (
            f"Email notification sent successfully "
            f"to {recipient}"
        )