from app.actions.mock import MockActionAdapter


class ActionDispatcher:
    def __init__(self):
        self.adapters = {
            "mock": MockActionAdapter(),
            "notification": MockActionAdapter(),
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