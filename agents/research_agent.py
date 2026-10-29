"""Agent 1: Research Agent

Collects information about the topic using knowledge retrieval tools and Sarvam AI.
Organizes findings systematically and structures them for the Analysis Agent.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, AgentResult
from tools.search_tool import KnowledgeRetriever
from sarvam_client import SarvamClient


RESEARCH_SYSTEM_PROMPT = """You are the RESEARCH AGENT in an elite multi-agent intelligence system.
Your mission is to gather, structure, and synthesize comprehensive, factual information about the assigned topic.

Responsibilities:
1. Define the topic with high technical rigor, precision, and clarity.
2. Outline key historical milestones and foundational breakthroughs.
3. Identify all primary application domains and real-world use cases.
4. Highlight technical architectures, underlying mechanisms, and operational principles.
5. Note technical limitations, open research challenges, and active areas of exploration.
6. Organize findings into clean, logical sections with clear markdown headings and bullet points.

Tone: Objective, thorough, academically rigorous, and empirically grounded.
Avoid superficial generalities; provide concrete examples, metrics, algorithms, or systems wherever relevant.
"""


class ResearchAgent(BaseAgent):
    """Collects, retrieves, and organizes in-depth information about a user's query."""

    def __init__(self, client: Optional[SarvamClient] = None):
        super().__init__(
            name="Research Agent",
            role="Information Gathering & Structuring",
            description="Collects comprehensive facts, background literature, and domain applications.",
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            client=client
        )

    def run(self, context: Dict[str, Any]) -> AgentResult:
        """Fetch background knowledge using retriever before running the LLM synthesis."""
        topic = context.get("topic", "")
        # Retrieve real background sources
        retrieval_data = KnowledgeRetriever.gather_background_context(topic, max_articles=3)
        context["retrieved_sources"] = retrieval_data
        
        # Now run the base agent with enriched context
        result = super().run(context)
        # Attach the retrieved sources into metadata
        result.metadata["retrieved_sources"] = retrieval_data.get("sources", [])
        return result

    def build_user_prompt(self, context: Dict[str, Any]) -> str:
        topic = context.get("topic", "")
        retrieval_data = context.get("retrieved_sources", {})
        sources = retrieval_data.get("sources", [])
        
        sources_text = ""
        if sources:
            sources_text = "\n\nRetrieved Reference Data:\n"
            for s in sources:
                sources_text += f"- Title: {s.get('title')}\n  Summary: {s.get('summary')}\n  URL: {s.get('url')}\n"

        return (
            f"Please conduct comprehensive research on the following user request:\n\n"
            f"TOPIC / INSTRUCTION: \"{topic}\"\n"
            f"{sources_text}\n"
            f"Please structure your research findings into:\n"
            f"1. Core Definitions & Conceptual Foundations\n"
            f"2. Historical Evolution & Breakthrough Milestones\n"
            f"3. Practical Applications & Real-World Use Cases (categorized by industry/field)\n"
            f"4. Technological Architectures & How It Operates\n"
            f"5. Current Constraints, Limitations & Open Research Questions\n"
            f"6. Primary Sources & References"
        )
