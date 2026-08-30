from app.actions.email import EmailActionAdapter


def main():
    adapter = EmailActionAdapter()

    result = adapter.execute(
        {
            "recipient": "kaiservignesh@gmail.com",
            "subject": "CogniOpsAI Test Notification",
            "body": (
                "This is a test email generated "
                "by the CogniOpsAI email adapter."
            ),
        }
    )

    print(result)


if __name__ == "__main__":
    main()