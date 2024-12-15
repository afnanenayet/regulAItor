# File: /Framework/agents/recommendation_agent.py

from autogen import ConversableAgent
import os
import logging

class RecommendationAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="recommendation_agent",
            system_message="You generate recommendations based on extracted violations and regulations.",
            llm_config={
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
        )

        self.register_reply(
            trigger=self._always_true_trigger, # Add a specific trigger string
            reply_func=self.handle_message,
            position=0
        )
    def _always_true_trigger(self, sender):
        # This trigger function always returns True
        return True
    def handle_message(self, *args, **kwargs):
      #  logging.debug(f"recommendation_agent: handle_message: messages={messages}, sender={sender}, kwargs={kwargs}")
        summary = self.context.get('summary', {})
        violated_terms = summary.get('violated_terms', [])
        regulation_texts = self.context.get("regulation_full_texts", {})
        similar_cases = self.context.get("similar_cases", [])
        # Use the LLM to generate recommendations
        prompt = f"""
Based on the following violations, regulation texts, and similar cases, generate recommendations to address each violation.

Violations:
{violated_terms}

Regulation Texts:
{regulation_texts}

Similar Cases:
{similar_cases}

Provide the recommendations in a clear and concise manner.
"""
        response = self.llm.generate(prompt)
        self.context["recommendations"] = response.strip()
        return {"role": "assistant", "content": "Recommendations generated."}