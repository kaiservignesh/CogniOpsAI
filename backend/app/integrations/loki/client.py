import os

import requests


class LokiClient:
    def __init__(self):
        self.api_url = os.getenv(
            "LOKI_API_URL",
            "http://localhost:3100",
        )
        self.mock = os.getenv(
            "LOKI_MOCK",
            "false",
        ).lower() == "true"

    def query_logs(
        self,
        query: str,
        limit: int = 100,
    ):
        if self.mock:
            return {
                "status": "success",
                "data": {
                    "resultType": "streams",
                    "result": [
                        {
                            "stream": {
                                "service": "payment-api",
                                "environment": "production",
                                "level": "ERROR",
                            },
                            "values": [
                                [
                                    "1754043300000000000",
                                    "Database connection timeout",
                                ],
                                [
                                    "1754043360000000000",
                                    "Connection pool exhausted",
                                ],
                            ],
                        }
                    ],
                },
            }

        response = requests.get(
            f"{self.api_url}/loki/api/v1/query_range",
            params={
                "query": query,
                "limit": limit,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()