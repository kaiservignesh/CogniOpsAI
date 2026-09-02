from app.actions.xmatters import (
    XMattersActionAdapter,
)


def main():
    adapter = XMattersActionAdapter()

    result = adapter.execute(
        {
            "recipient": "operations",
            "subject": "CogniOpsAI Test",
            "message": (
                "Test xMatters notification "
                "from CogniOpsAI."
            ),
        }
    )

    print(result)


if __name__ == "__main__":
    main()