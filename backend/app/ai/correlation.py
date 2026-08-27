from app.ai.vector_store import VectorStore


class HistoricalCorrelation:
    def __init__(self):
        self.vector_store = VectorStore()

    def calculate_similarity_score(
        self,
        situation_context: dict,
    ) -> float:
        results = self.vector_store.search_similar(
            query=self._build_query(
                situation_context
            ),
            limit=1,
        )

        distances = results.get(
            "distances",
            [[]],
        )

        if not distances or not distances[0]:
            return 0.0

        distance = distances[0][0]

        # ChromaDB distance is converted into a
        # simple 0-100 similarity score.
        similarity = max(
            0.0,
            100.0 - (float(distance) * 50.0),
        )

        return min(similarity, 100.0)

    @staticmethod
    def _build_query(
        situation_context: dict,
    ) -> str:
        alerts = situation_context.get(
            "alerts",
            [],
        )

        alert_titles = " ".join(
            alert.get("title", "")
            for alert in alerts
        )

        return (
            f"{situation_context.get('title', '')} "
            f"{situation_context.get('description', '')} "
            f"{situation_context.get('service', '')} "
            f"{situation_context.get('environment', '')} "
            f"{alert_titles}"
        )