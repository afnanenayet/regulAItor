from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import autogen
from autogen import AssistantAgent
from dsp import OpenAIVectorizer
import dspy
from dspy.retrieve.qdrant_rm import QdrantRM
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Payload, PayloadSchemaParams, VectorParams
from sentence_transformers import SentenceTransformer

from regulaitor.Framework.config import QdrantConfig
from regulaitor.Framework.settings import GenerateSummary, InputGuardrail


class FDAWarningLetterSystem:
    def __init__(
        self,
        config_path: Path,
        qdrant_config: Optional[QdrantConfig] = None,
        max_rounds: int = 12,
    ):
        """
        Args:
            config_path: Either a file path to a config file that can be read by autogen, or None.
              If this is set to `None`, then the config file path will be pulled from an
              environment variable.
        """
        self.qdrant_config = qdrant_config or QdrantConfig()
        self.max_rounds = max_rounds
        self.config_list = autogen.config_list_from_json(str(config_path))
        logger.info(f"Using config list {self.config_list}")
        self.embedding_model = SentenceTransformer("all-mpnet-base-v2")
        self.setup_qdrant()
        self.setup_llm_config()
        self.initialize_agents()

    def setup_qdrant(self) -> None:
        self.client = QdrantClient(url=self.qdrant_config.url)

        # Ensure collection exists before attempting deletion
        if self.client.collection_exists(self.qdrant_config.collection_name):
            try:
                self.client.delete_collection(self.qdrant_config.collection_name)
            except Exception as e:
                logger.warning(f"Collection deletion failed: {e}")

        self.client.create_collection(
            collection_name=self.qdrant_config.collection_name,
            vectors_config=VectorParams(
                size=self.qdrant_config.vector_size,
                distance=self.qdrant_config.distance,
            ),
            # payload_schema={
            #     "recommendations": dict(data_type="text"),
            #     "warning_letter": dict(data_type="text"),
            #     "summary": dict(data_type="text"),
            # },
        )

    def setup_llm_config(self) -> None:
        self.llm_config = {
            "config_list": self.config_list,
            "timeout": 60,
            "temperature": 0.5,
            "seed": 1234,
        }

        # Configure DSPy
        turbo = dspy.LM(model="openai/gpt-4o")
        vectorizer = OpenAIVectorizer(model="text-embedding-ada-002")

        # Initialize Qdrant retriever for DSPy
        qdrant_retriever = QdrantRM(
            qdrant_client=self.client,
            qdrant_collection_name=self.qdrant_config.collection_name,
            vectorizer=vectorizer,
            document_field="warning_letter",
        )

        dspy.settings.configure(lm=turbo, rm=qdrant_retriever)

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence-transformers"""
        return self.embedding_model.encode(text).tolist()

    def initialize_agents(self) -> None:
        # Input Guardrail
        self.input_guardrail = dspy.Predict(InputGuardrail)

        # Agent 1: Summary Extractor (using DSPy)
        summary_prompt = """Read the FDA warning letter and extract a one-paragraph summary that lists:
                            1. All violated terms and regulations (with specific references)
                            2. Compliance issues alleged in the document
                            3. Brief description of each violation
                            4. Impact on pharmaceutical standards compliance
                            Make the summary concise yet comprehensive, capturing all key compliance failures."""

        self.summary_generator = dspy.ChainOfThought(
            GenerateSummary, prompt_template=summary_prompt
        )

        # Agent 2: Similar Cases Retriever
        self.retrieval_agent = AssistantAgent(
            name="Similar_Cases_Retriever",
            system_message="""Analyze the retrieved similar cases and their recommendations.
                            Focus on cases with similar violations and extract relevant recommendations.""",
            llm_config=self.llm_config,
        )

        # Agent 3: Regulation Extractor
        self.regulation_agent = AssistantAgent(
            name="Regulation_Extractor",
            system_message="""Analyze the FDA warning letter and extract only the specific law
                            or regulation references cited as violated (e.g., '21 CFR 211.165(a)'). 
                            Return these as a clean list without additional text.""",
            llm_config=self.llm_config,
        )

        # Agent 4: Law Provider. Here we need to define a new funtion to provide the law content
        self.law_provider = AssistantAgent(
            name="Law_Provider",
            system_message="""Retrieve the full text of the laws and regulations cited in the warning letter. 
                                Provide the detailed content of each law or regulation referenced in the warning letter.""",
            llm_config=self.llm_config,
        )

        # Agent 5: Corrective Action Generator
        self.corrective_agent = AssistantAgent(
            name="Corrective_Action_Generator",
            system_message="""Generate corrective actions based on the extracted violations, similar cases, and law content. 
                                Provide a detailed plan to address the compliance failures and prevent future violations.""",
            llm_config=self.llm_config,
        )

        # Agent 6: Review Agent
        self.review_agent = AssistantAgent(
            name="Review_Agent",
            system_message="""
                 Evaluate the proposed corrective actions to ensure they are comprehensive, proper, and fully address all regulatory violations outlined in the original warning letter. 
                                  Provide your response in the format: 
                                    - 'Approved: Yes/No' 
                                    - 'Feedback: <Your detailed feedback>'.
                 """,
            llm_config=self.llm_config,
        )

    def retrieve_similar_cases(
        self, summary_embedding: List[float]
    ) -> List[Dict[str, Any]]:
        """Retrieve similar cases based on summary embedding"""
        search_results = self.client.search(
            collection_name=self.qdrant_config.collection_name,
            query_vector=summary_embedding,
            limit=5,
            with_payload=True,
        )

        return [
            {
                "warning_letter": result.payload.get("warning_letter", ""),
                "recommendations": result.payload.get("recommendations", ""),
                "summary": result.payload.get("summary", ""),
                "score": result.score,
            }
            for result in search_results
        ]

    # This function is not used here, instead, we use the one in the state_machine
    def process_warning_letter(self, warning_letter: str) -> Dict[str, Any]:
        results = {}

        # Step 1: Input Guardrail Check
        guardrail_check = self.input_guardrail(user_input=warning_letter)
        if guardrail_check.should_block == "Yes":
            logger.warning(f"Input blocked: {guardrail_check.reason}")
            return {"error": guardrail_check.reason}

        # Step 2: Extract Summary using DSPy
        logger.info("Extracting violation summary...")
        summary_prediction = self.summary_generator(warning_letter=warning_letter)
        results["summary"] = summary_prediction.summary

        # Generate embedding for the summary
        summary_embedding = self.get_embedding(results["summary"])

        # Step 3: Retrieve Similar Cases using summary embedding
        logger.info("Retrieving similar warning letters based on summary...")
        similar_cases = self.retrieve_similar_cases(summary_embedding)

        # Process retrieved cases with Agent 2
        similar_cases_analysis = self.retrieval_agent.generate_response(
            {"summary": results["summary"], "similar_cases": similar_cases}
        )
        results["similar_cases"] = {
            "cases": similar_cases,
            "analysis": similar_cases_analysis,
        }

        # Step 4: Extract Regulations
        logger.info("Extracting regulation references...")
        regulations = self.regulation_agent.generate_response(warning_letter)
        results["regulations"] = regulations

        # Step 5: Get Law Content. Here we need to define a new funtion to provide the law content
        logger.info("Retrieving full law content...")
        law_content = self.law_provider.generate_response(regulations)
        results["law_content"] = law_content

        # Step 6: Generate Corrective Actions
        logger.info("Generating corrective actions...")
        corrective_action = self.corrective_agent.generate_response(
            {
                "warning_letter": warning_letter,
                "similar_cases": similar_cases_analysis,
                "law_content": law_content,
            }
        )
        results["corrective_action"] = corrective_action

        # Step 7: Review and Validate
        logger.info("Reviewing corrective actions...")
        max_revision_attempts = 3
        revision_count = 0

        review_result = self.review_agent.generate_response(
            {
                "warning_letter": warning_letter,
                "corrective_action": corrective_action,
            }
        )

        while (
            not review_result.get("Approved", "No") == "Yes"
            and revision_count < max_revision_attempts
        ):
            logger.info(
                f"Revision attempt {revision_count + 1}: Improving corrective actions..."
            )

            corrective_action = self.corrective_agent.generate_response(
                {
                    "warning_letter": warning_letter,
                    "similar_cases": similar_cases_analysis,
                    "law_content": law_content,
                    "previous_feedback": review_result.get("feedback", ""),
                }
            )

            review_result = self.review_agent.generate_response(
                {
                    "warning_letter": warning_letter,
                    "corrective_action": corrective_action,
                }
            )

            revision_count += 1

        results["corrective_action"] = corrective_action
        results["review_result"] = review_result
        results["revision_count"] = revision_count

        if not review_result.get("approved", "No") == "Yes":
            logger.warning("Maximum revision attempts reached without full approval")

        return results

    def reset_agents(self) -> None:
        """Reset all agents to their initial state"""
        for agent in [
            self.summary_generator,
            self.retrieval_agent,
            self.regulation_agent,
            self.law_provider,
            self.corrective_agent,
            self.review_agent,
        ]:
            agent.reset()
