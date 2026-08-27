import os

import chromadb


class VectorStore:
    def __init__(self):
        persist_directory = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            "./chroma_data",
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name="incident_knowledge"
        )

    def add_situation(
        self,
        situation_id: int,
        document: str,
        metadata: dict | None = None,
    ):
        self.collection.upsert(
            ids=[str(situation_id)],
            documents=[document],
            metadatas=[metadata or {}],
        )

    def search_similar(
        self,
        query: str,
        limit: int = 3,
    ):
        return self.collection.query(
            query_texts=[query],
            n_results=limit,
        )