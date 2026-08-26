from app.ai.client import OllamaClient


def main():
    client = OllamaClient()

    response = client.generate(
        "Explain in one sentence what an alert is."
    )

    print(response)


if __name__ == "__main__":
    main()