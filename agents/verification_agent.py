"""Agent 3: Verification Agent

Checks factual claims against evidence and logical consistency.
Identifies missing or unsupported information.
Requests corrections, caveats, and refinements before the Writer Agent creates the final report.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from sarvam_client import SarvamClient


VERIFICATION_SYSTEM_PROMPT = """You are the VERIFICATION AGENT in an advanced multi-agent research pipeline.
Your mission is to act as an uncompromising Fact-Checker, Evidence Auditor, and Scientific Peer Reviewer.

Responsibilities:
1. Scrutinize all factual statements, dates, claims, and figures in the Research and Analysis dossiers.
2. Cross-reference claims against grounded evidence, highlighting verified vs. unverified assertions.
3. Detect hallucinations, over-generalizations, hype, or conflations (e.g., Narrow AI vs AGI, theoretical vs deployed).
4. Pinpoint missing perspectives, neglected counterarguments, or unaddressed risks (e.g., environmental cost, regulatory compliance).
5. Produce a Verification Scorecard:
   - [VERIFIED]: Solid, well-documented facts.
   - [CAVEAT / NUANCED]: Claims that need qualifications, context, or tempered language.
   - [UNSUPPORTED / SPECULATIVE]: Questionable or unproven statements.
6. Provide clear, actionable Directives & Mandatory Corrections for the Writer Agent.

Tone: Rigorous, vigilant, impartial, and constructive.
"""


class VerificationAgent(BaseAgent):
    """Verifies evidence, audits claims, and issues correction directives for the final report."""

    def __init__(self, client: Optional[SarvamClient] = None):
        super().__init__(
            name="Verification Agent",
            role="Evidence Auditing & Quality Assurance",
            description="Fact-checks claims, identifies blind spots, and formulates correction directives.",
            system_prompt=VERIFICATION_SYSTEM_PROMPT,
            client=client
        )

    def build_user_prompt(self, context: Dict[str, Any]) -> str:
        topic = context.get("topic", "")
        research_output = context.get("research_output", "")
        analysis_output = context.get("analysis_output", "")
        retrieved_data = context.get("retrieved_sources", [])
        if isinstance(retrieved_data, dict):
            sources = retrieved_data.get("sources", [])
        elif isinstance(retrieved_data, list):
            sources = retrieved_data
        else:
            sources = []

        sources_ref = ""
        if sources:
            sources_ref = "\n\nGround Truth Reference Highlights:\n"
            for s in sources:
                title = s.get("title", "Reference") if isinstance(s, dict) else str(s)
                summary = s.get("summary", "")[:300] if isinstance(s, dict) else ""
                sources_ref += f"- {title}: {summary}...\n"

        return (
            f"Please conduct an evidence verification audit on the following research package for: \"{topic}\"\n"
            f"{sources_ref}\n"
            f"--- RESEARCH DOSSIER ---\n"
            f"{research_output}\n"
            f"--- END RESEARCH DOSSIER ---\n\n"
            f"--- ANALYSIS DOSSIER ---\n"
            f"{analysis_output}\n"
            f"--- END ANALYSIS DOSSIER ---\n\n"
            f"Provide your verification audit with the following mandatory structure:\n"
            f"1. Verification Scorecard (Categorize key claims under [VERIFIED], [CAVEAT/NUANCED], or [UNSUPPORTED])\n"
            f"2. Identification of Blind Spots & Missing Critical Dimensions (What crucial elements were omitted?)\n"
            f"3. Risk & Hallucination Assessment (Check for hyperbole or unwarranted technical optimism)\n"
            f"4. Concrete Editorial Directives for the Writer Agent (Specific mandatory inclusions and corrections)"
        )
