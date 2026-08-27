from app.ai.client import OllamaClient
from app.ai.vector_store import VectorStore
from app.ai.prompts import (
    build_recommendation_prompt,
    build_root_cause_prompt,
    build_situation_summary_prompt,
)


class AIService:
    def __init__(self):
        self.client = OllamaClient()
        self.vector_store = VectorStore()

    def summarize_situation(
        self,
        situation_context: dict,
    ) -> str:
        prompt = build_situation_summary_prompt(
            situation_context
        )

        return self.client.generate(prompt)

    # def analyze_root_cause(
    #     self,
    #     situation_context: dict,
    # ) -> str:
    #     prompt = build_root_cause_prompt(
    #         situation_context
    #     )

    #     return self.client.generate(prompt)

    def analyze_root_cause(
        self,
        situation_context: dict,
    ) -> str:
        similar = self.find_similar_situations(
            situation_context,
            limit=3,
        )

        historical_context = ""

        documents = similar.get(
            "documents",
            [[]],
        )

        distances = similar.get(
            "distances",
            [[]],
        )

        if documents and documents[0]:
            context_parts = []

            for index, document in enumerate(
                documents[0]
            ):
                distance = None

                if distances and distances[0]:
                    distance = distances[0][index]

                context_parts.append(
                    f"Historical Situation {index + 1}:\n"
                    f"{document}\n"
                    f"Similarity Distance: {distance}"
                )

            historical_context = "\n\n".join(
                context_parts
            )

        prompt = build_root_cause_prompt(
            situation_context=situation_context,
            historical_context=historical_context,
        )

        return self.client.generate(prompt)

    def recommend_actions(
        self,
        situation_context: dict,
    ) -> str:
        similar = self.find_similar_situations(
            situation_context,
            limit=3,
        )

        historical_context = ""

        documents = similar.get(
            "documents",
            [[]],
        )

        distances = similar.get(
            "distances",
            [[]],
        )

        if documents and documents[0]:
            context_parts = []

            for index, document in enumerate(
                documents[0]
            ):
                distance = None

                if distances and distances[0]:
                    distance = distances[0][index]

                context_parts.append(
                    f"Historical Situation {index + 1}:\n"
                    f"{document}\n"
                    f"Similarity Distance: {distance}"
                )

            historical_context = "\n\n".join(
                context_parts
            )

        prompt = build_recommendation_prompt(
            situation_context=situation_context,
            historical_context=historical_context,
        )

        return self.client.generate(prompt)

    def store_situation(
        self,
        situation_context: dict,
    ):
        alerts = situation_context.get(
            "alerts",
            [],
        )

        alert_text = "\n".join(
            alert["title"]
            for alert in alerts
        )

        document = (
            f"Situation: "
            f"{situation_context.get('title')}\n"
            f"Severity: "
            f"{situation_context.get('severity')}\n"
            f"Service: "
            f"{situation_context.get('service')}\n"
            f"Environment: "
            f"{situation_context.get('environment')}\n"
            f"Description: "
            f"{situation_context.get('description')}\n"
            f"Alerts:\n{alert_text}"
        )

        self.vector_store.add_situation(
            situation_id=situation_context["id"],
            document=document,
            metadata={
                "severity": situation_context.get(
                    "severity"
                ),
                "service": situation_context.get(
                    "service"
                ),
                "environment": situation_context.get(
                    "environment"
                ),
            },
        )

        return {
            "status": "stored",
            "situation_id": situation_context["id"],
        }

    def find_similar_situations(
        self,
        situation_context: dict,
        limit: int = 3,
    ):
        query = (
            f"{situation_context.get('title')} "
            f"{situation_context.get('description')} "
            f"{situation_context.get('service')} "
            f"{situation_context.get('environment')}"
        )

        return self.vector_store.search_similar(
            query=query,
            limit=limit,
        )