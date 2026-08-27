from app.ai.vector_store import VectorStore


def main():
    store = VectorStore()

    store.add_situation(
        situation_id=1001,
        document=(
            "Payment API experienced high CPU usage "
            "and database connection timeouts."
        ),
        metadata={
            "severity": "Critical",
            "service": "payment-api",
            "environment": "production",
        },
    )

    results = store.search_similar(
        "Payment service CPU and database issue",
        limit=3,
    )

    print(results)


if __name__ == "__main__":
    main()