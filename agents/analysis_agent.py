"""Agent 2: Analysis Agent

Reads the findings compiled by the Research Agent.
Extracts core patterns, analyzes strategic significance, evaluates trade-offs,
and categorizes systemic impact across industries.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from sarvam_client import SarvamClient


ANALYSIS_SYSTEM_PROMPT = """You are the ANALYSIS AGENT in a high-performance multi-agent research team.
Your mission is to perform deep critical, structural, and strategic analysis on raw research data.

Responsibilities:
1. Distill key patterns, value drivers, and paradigm shifts from the research findings.
2. Conduct an in-depth comparative impact analysis across application sectors (e.g. Healthcare, Finance, Governance, Engineering).
3. Evaluate second-order implications: economic disruption, job market shifts, privacy, and systemic risk.
4. Assess strengths vs. vulnerabilities (e.g., hallucination, data poisoning, compute centralization, bias).
5. Identify high-leverage opportunities vs. overhyped claims.
6. Provide clear analytical takeaways that go beyond merely restating the facts.

Tone: Analytical, discerning, incisive, and balanced. Challenge assumptions where appropriate.
"""


class AnalysisAgent(BaseAgent):
    """Analyzes, interprets, and critiques the findings gathered by the Research Agent."""

    def __init__(self, client: Optional[SarvamClient] = None):
        super().__init__(
            name="Analysis Agent",
            role="Critical Analysis & Synthesis",
            description="Extracts patterns, evaluates strategic implications, and identifies trade-offs.",
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            client=client
        )

    def build_user_prompt(self, context: Dict[str, Any]) -> str:
        topic = context.get("topic", "")
        research_output = context.get("research_output", "")

        return (
            f"Analyze the research findings below regarding the topic: \"{topic}\"\n\n"
            f"--- RESEARCH AGENT FINDINGS ---\n"
            f"{research_output}\n"
            f"--- END OF RESEARCH FINDINGS ---\n\n"
            f"Please conduct an in-depth analytical assessment with the following sections:\n"
            f"1. Core Strategic Insights & Paradigm Shifts (What fundamental transformations are underway?)\n"
            f"2. Multi-Sector Application Impact Matrix (Evaluate maturity, high-impact drivers, and friction for key sectors)\n"
            f"3. Comparative Trade-offs & Bottlenecks (Benefits vs. Cost, Latency, Interpretability, Infrastructure)\n"
            f"4. Societal, Ethical & Regulatory Implications (Data governance, liability, systemic risks)\n"
            f"5. Key Analytical Takeaways (Actionable conclusions for stakeholders)"
        )
