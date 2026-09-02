from app.actions.servicenow import (
    ServiceNowActionAdapter,
)


def main():
    adapter = ServiceNowActionAdapter()

    result = adapter.execute(
        {
            "title": "Test CogniOpsAI Incident",
            "description": (
                "Test incident generated "
                "by CogniOpsAI."
            ),
            "severity": "High",
            "service": "payment-api",
            "environment": "production",
        }
    )

    print(result)


if __name__ == "__main__":
    main()