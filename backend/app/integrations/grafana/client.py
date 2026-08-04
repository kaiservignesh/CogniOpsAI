import os

import requests


class GrafanaClient:
    def __init__(self):
        self.api_url = os.getenv(
            "GRAFANA_API_URL",
            "http://localhost:3000",
        )
        self.api_token = os.getenv(
            "GRAFANA_API_TOKEN"
        )
        self.mock = os.getenv(
            "GRAFANA_MOCK",
            "false",
        ).lower() == "true"

    def get_alerts(self):
        if self.mock:
            return [
                {
                    "name": "High CPU Usage",
                    "description": (
                        "CPU usage exceeded 95%"
                    ),
                    "severity": "Critical",
                    "labels": {
                        "environment": "production",
                        "service": "payment-api",
                    },
                },
                {
                    "name": "High Memory Usage",
                    "description": (
                        "Memory usage exceeded 90%"
                    ),
                    "severity": "High",
                    "labels": {
                        "environment": "production",
                        "service": "payment-api",
                    },
                },
            ]

        if not self.api_token:
            raise ValueError(
                "GRAFANA_API_TOKEN is not configured"
            )

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        }

        response = requests.get(
            f"{self.api_url}/api/v1/provisioning/alert-rules",
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()