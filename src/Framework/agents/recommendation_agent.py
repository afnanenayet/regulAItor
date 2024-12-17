from autogen import ConversableAgent
import os
import logging
from openai import OpenAI


class RecommendationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="recommendation_agent",
            system_message="You generate recommendations based on extracted violations and regulations.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )

        self.register_reply(
            trigger=self._always_true_trigger,
            reply_func=self.handle_message,
            position=0,
        )
        self.client = OpenAI(api_key=self.llm_config["api_key"])

    def _always_true_trigger(self, sender):
        return True

    def handle_message(self, *args, **kwargs):
        summary = self.context.get("summary", {})
        violated_terms = summary.get("violated_terms", [])
        regulation_texts = self.context.get("regulation_full_texts", {})
        similar_cases = self.context.get("similar_cases", [])

        messages = [
            {
                "role": "system",
                "content": "You generate recommendations based on extracted violations and regulations.",
            },
            {
                "role": "user",
                "content": f"""
Based on the following violations, regulation texts, and similar cases, generate recommendations to address each violation.

Violations:
{violated_terms}

Regulation Texts:
{regulation_texts}

Similar Cases:
{similar_cases}

Provide the recommendations in a clear and concise manner.
""",
            },
        ]

        # Use the chat completions endpoint instead of completions
        response = self.client.chat.completions.create(
            model=self.llm_config["model"],
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )

        self.context["recommendations"] = response.choices[0].message.content.strip()
        return {"role": "assistant", "content": "Recommendations generated."}
