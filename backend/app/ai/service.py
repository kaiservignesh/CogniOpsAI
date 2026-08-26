from app.ai.client import OllamaClient
from app.ai.prompts import (
    build_root_cause_prompt,
    build_situation_summary_prompt,
)


class AIService:
    def __init__(self):
        self.client = OllamaClient()

    def summarize_situation(
        self,
        situation_context: dict,
    ) -> str:
        prompt = build_situation_summary_prompt(
            situation_context
        )

        return self.client.generate(prompt)

    def analyze_root_cause(
        self,
        situation_context: dict,
    ) -> str:
        prompt = build_root_cause_prompt(
            situation_context
        )

        return self.client.generate(prompt)