import os

import requests


class NewRelicClient:
    def __init__(self):
        self.api_url = os.getenv(
            "NEW_RELIC_API_URL",
            "https://api.newrelic.com",
        )
        self.api_key = os.getenv("NEW_RELIC_API_KEY")
        self.mock = os.getenv(
            "NEW_RELIC_MOCK",
            "false",
        ).lower() == "true"

    def get_alerts(self):
        if self.mock:
            return {
                "violations": [
                    {
                        "description": "CPU usage exceeded 95%",
                        "priority": "Critical",
                        "policy_name": "Production CPU Policy",
                        "entity": "payment-service",
                    },
                    {
                        "description": "Memory usage exceeded 90%",
                        "priority": "High",
                        "policy_name": "Production Memory Policy",
                        "entity": "payment-service",
                    },
                ]
            }

        if not self.api_key:
            raise ValueError(
                "NEW_RELIC_API_KEY is not configured"
            )

        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{self.api_url}/v2/alerts_violations.json",
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()