from app.actions.base import ActionAdapter


class MockActionAdapter(ActionAdapter):
    def execute(
        self,
        payload: dict,
    ) -> str:
        return (
            "Mock action executed successfully. "
            f"Payload: {payload}"
        )