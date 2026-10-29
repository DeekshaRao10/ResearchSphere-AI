"""Agent 4: Writer Agent

Combines the verified findings, analysis insights, and correction directives.
Synthesizes all multi-agent contributions into a polished, authoritative final report.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from sarvam_client import SarvamClient


WRITER_SYSTEM_PROMPT = """You are the WRITER AGENT in a state-of-the-art multi-agent research consortium.
Your mission is to synthesize all upstream agent outputs (Research, Analysis, and Verification)
into an authoritative, publication-quality Executive Research Report.

Responsibilities:
1. Harmonize factual findings (Research), critical insights (Analysis), and audited facts (Verification).
2. Faithfully follow the editorial directives, caveats, and corrections mandated by the Verification Agent.
3. Structure the final report with exceptional aesthetic and intellectual coherence:
   - Clear Markdown hierarchy (H1, H2, H3, callouts, bullet points).
   - Executive Summary delivering instant value.
   - Deep-dive sections explaining theoretical foundations and application domains.
   - Comprehensive balanced assessment of benefits, risks, and governance.
   - Transparent Multi-Agent Audit Trail detailing the verification outcomes.
4. Eliminate redundant phrasing and ensure smooth transitions between sections.

Tone: Authoritative, polished, lucid, engaging, and professional.
"""


class WriterAgent(BaseAgent):
    """Produces the final consolidated research report incorporating all agent inputs."""

    def __init__(self, client: Optional[SarvamClient] = None):
        super().__init__(
            name="Writer Agent",
            role="Synthesis & Final Report Generation",
            description="Compiles verified findings, analytical insights, and corrections into a comprehensive report.",
            system_prompt=WRITER_SYSTEM_PROMPT,
            client=client
        )

    def build_user_prompt(self, context: Dict[str, Any]) -> str:
        topic = context.get("topic", "")
        research_output = context.get("research_output", "")
        analysis_output = context.get("analysis_output", "")
        verification_output = context.get("verification_output", "")

        return (
            f"Please synthesize and write the definitive Final Research Report on:\n"
            f"TOPIC: \"{topic}\"\n\n"
            f"=== 1. RESEARCH AGENT FINDINGS ===\n"
            f"{research_output}\n\n"
            f"=== 2. ANALYSIS AGENT INSIGHTS ===\n"
            f"{analysis_output}\n\n"
            f"=== 3. VERIFICATION AGENT AUDIT & DIRECTIVES ===\n"
            f"{verification_output}\n\n"
            f"--- MANDATORY WRITING INSTRUCTIONS ---\n"
            f"Format the final report in clean, professional Markdown with these comprehensive sections:\n"
            f"# [Title of the Research Report]\n"
            f"**Multi-Agent Research Intelligence System | Powered by Sarvam AI**\n\n"
            f"## Executive Summary\n"
            f"## 1. Introduction & Conceptual Foundations\n"
            f"## 2. Core Technological Architecture & How It Works\n"
            f"## 3. Comprehensive Breakdown of Applications (Detailed by Sector)\n"
            f"## 4. Strategic Analysis, Challenges & Ethical Considerations (Address Verification Caveats)\n"
            f"## 5. Multi-Agent Verification & Evidence Audit Trail (Summary of Verification Scorecard)\n"
            f"## 6. Strategic Recommendations & Future Outlook\n"
            f"## 7. Citations & References\n"
        )
