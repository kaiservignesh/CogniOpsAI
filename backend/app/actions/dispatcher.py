from app.actions.email import EmailActionAdapter
from app.actions.mock import MockActionAdapter
from app.actions.servicenow import (
    ServiceNowActionAdapter,
)
from app.actions.xmatters import (
    XMattersActionAdapter,
)


class ActionDispatcher:
    def __init__(self):
        self.adapters = {
            "mock": MockActionAdapter(),
            "notification": MockActionAdapter(),
            "email": EmailActionAdapter(),
            "servicenow": ServiceNowActionAdapter(),
            "xmatters": XMattersActionAdapter(),
        }

    def dispatch(
        self,
        action_type: str | None,
        payload: dict,
    ) -> str:
        normalized_type = (
            action_type or "mock"
        ).lower()

        adapter = self.adapters.get(
            normalized_type
        )

        if adapter is None:
            raise ValueError(
                f"Unsupported action type: "
                f"{action_type}"
            )

        return adapter.execute(payload)