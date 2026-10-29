"""Sarvam AI Client wrapper for Chat Completions API.

Supports Sarvam AI endpoints (v1 and v2), custom authentication headers,
error handling, and an intelligent offline simulation fallback for testing.
"""

import json
import logging
from typing import Dict, List, Any, Optional
import requests

from config import Config

logger = logging.getLogger("SarvamClient")


class SarvamAPIError(Exception):
    """Custom exception for Sarvam AI API errors."""
    pass


class SarvamClient:
    """Interface to communicate with Sarvam AI's LLM Chat Completions API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        demo_mode: Optional[bool] = None,
    ):
        self.api_key = api_key if api_key is not None else Config.SARVAM_API_KEY
        self.model = model if model is not None else Config.SARVAM_MODEL
        self.base_url = (base_url if base_url is not None else Config.SARVAM_BASE_URL).rstrip("/")
        self.temperature = temperature if temperature is not None else Config.SARVAM_TEMPERATURE
        
        # If demo_mode is explicitly set or if no valid API key is present
        if demo_mode is not None:
            self.demo_mode = demo_mode
        else:
            self.demo_mode = Config.DEMO_MODE or not self._is_valid_key(self.api_key)

    @staticmethod
    def _is_valid_key(key: Optional[str]) -> bool:
        if not key:
            return False
        clean = key.strip().lower()
        return clean not in ("your_sarvam_api_key_here", "none", "", "mock", "demo")

    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Sarvam AI with a minimal prompt."""
        if self.demo_mode:
            return {
                "success": True,
                "mode": "demo",
                "message": "Running in Demo/Simulation Mode (No active Sarvam API key required)."
            }
        
        test_messages = [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": "Respond with 'Connected'"}
        ]
        try:
            res = self.generate(test_messages, max_tokens=10)
            return {
                "success": True,
                "mode": "live",
                "message": f"Successfully connected to Sarvam AI ({self.model}). Response: {res['content'].strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "mode": "error",
                "message": f"Sarvam AI connection failed: {str(e)}"
            }

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        agent_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send chat completion request to Sarvam AI or route to simulator if demo_mode is True."""
        if self.demo_mode:
            return self._simulate_response(messages, agent_role)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": Config.MAX_TOKENS if max_tokens is None else max_tokens,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                return {
                    "content": content,
                    "usage": usage,
                    "model": data.get("model", self.model),
                    "mode": "live"
                }
            elif response.status_code in (401, 403):
                raise SarvamAPIError(
                    f"Sarvam AI Authentication Failed (Status {response.status_code}). "
                    f"Please verify your SARVAM_API_KEY in .env or the UI."
                )
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                raise SarvamAPIError(f"Sarvam AI API error {response.status_code}: {error_msg}")

        except requests.exceptions.RequestException as req_err:
            raise SarvamAPIError(f"Network error connecting to Sarvam AI at {url}: {req_err}")

    def _simulate_response(self, messages: List[Dict[str, str]], agent_role: Optional[str]) -> Dict[str, Any]:
        """High-fidelity contextual simulation for offline testing or demonstration without an API key.
        Dynamically adapts to ANY topic entered by the user using live retrieved reference facts.
        """
        import re
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_msg = m.get("content", "")
                break

        # Extract topic and reference context from prompt
        ctx = self._extract_topic_and_context(user_msg)

        role = (agent_role or "").lower()
        if "research" in role or "gathering" in role:
            content = self._dynamic_research_output(ctx, user_msg)
        elif "analysis" in role or "critical" in role:
            content = self._dynamic_analysis_output(ctx, user_msg)
        elif "verification" in role or "audit" in role:
            content = self._dynamic_verification_output(ctx, user_msg)
        elif "writer" in role or "synthesis" in role or "report" in role:
            content = self._dynamic_writer_output(ctx, user_msg)
        else:
            content = f"Simulated multi-agent response for {ctx['clean_topic']} processed by Sarvam AI model ({self.model})."

        return {
            "content": content,
            "usage": {
                "prompt_tokens": len(user_msg) // 4,
                "completion_tokens": len(content) // 4,
                "total_tokens": (len(user_msg) + len(content)) // 4
            },
            "model": f"{self.model}-simulated",
            "mode": "demo"
        }

    def _extract_topic_and_context(self, user_msg: str) -> Dict[str, Any]:
        """Extracts the query topic and any retrieved reference snippets from the prompt."""
        import re
        topic = ""
        topic_match = re.search(r'TOPIC(?:\s*/\s*INSTRUCTION)?:\s*["\']?([^"\'\n\r]+)["\']?', user_msg, re.IGNORECASE)
        if topic_match:
            topic = topic_match.group(1).strip()
        elif "regarding the topic:" in user_msg:
            m = re.search(r'regarding the topic:\s*["\']?([^"\'\n\r]+)["\']?', user_msg, re.IGNORECASE)
            if m:
                topic = m.group(1).strip()
        elif "for:" in user_msg:
            m = re.search(r'for:\s*["\']?([^"\'\n\r]+)["\']?', user_msg, re.IGNORECASE)
            if m:
                topic = m.group(1).strip()

        if not topic:
            lines = [l.strip() for l in user_msg.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("===")]
            topic = lines[0][:80] if lines else "Research Topic"

        # Clean topic string: strip verbs like "Research", "Explain", etc.
        clean_topic = re.sub(r'^(research|explain|study|analyze|investigate|what is|tell me about)\s+', '', topic, flags=re.IGNORECASE).strip()
        clean_topic = clean_topic.rstrip('.?!')
        if not clean_topic:
            clean_topic = topic

        # Extract references present in the prompt
        references = []
        ref_blocks = re.findall(r'- Title:\s*([^\n]+)\n\s*Summary:\s*([^\n]+)(?:\n\s*URL:\s*([^\n]+))?', user_msg)
        for t, s, u in ref_blocks:
            references.append({
                "title": t.strip(),
                "summary": s.strip(),
                "url": u.strip() if u else f"https://en.wikipedia.org/wiki/{t.strip().replace(' ', '_')}"
            })

        # If no references were in prompt, attempt quick retrieval so facts are genuine
        if not references:
            try:
                from tools.search_tool import KnowledgeRetriever
                bg = KnowledgeRetriever.gather_background_context(clean_topic, max_articles=2)
                references = bg.get("sources", [])
            except Exception:
                pass

        primary_fact = ""
        if references:
            primary_fact = references[0].get("summary", "")

        return {
            "topic": topic,
            "clean_topic": clean_topic,
            "references": references,
            "primary_fact": primary_fact
        }

    def _dynamic_research_output(self, ctx: Dict[str, Any], prompt: str) -> str:
        topic = ctx["clean_topic"]
        fact = ctx["primary_fact"] or f"{topic} is an active domain of scientific, technological, and industrial investigation."
        refs = ctx["references"]

        refs_text = ""
        if refs:
            for r in refs:
                refs_text += f"- **{r.get('title')}**: {r.get('summary')[:160]}... ([Source]({r.get('url')}))\n"
        else:
            refs_text = f"- **{topic} Archive**: Reference articles and technical documentation.\n"

        return (
            f"### 1. Topic Definition & Core Principles\n"
            f"**{topic}** represents a fundamental domain of contemporary inquiry. "
            f"{fact}\n\n"
            f"At its core, {topic} relies on systematic principles, structural models, and quantitative methodologies "
            f"designed to address complex challenges, optimize processes, and unlock new functional capabilities.\n\n"
            f"### 2. Historical & Foundational Milestones\n"
            f"- **Foundational Era**: Initial theoretical formulation, fundamental principles, and early mathematical/empirical proofs.\n"
            f"- **Exploratory Breakthroughs**: Translation of theoretical hypotheses into experimental prototypes and early architectures.\n"
            f"- **Industrial Scaling**: Transition from controlled laboratory settings into commercial and enterprise infrastructures.\n"
            f"- **Modern Paradigm**: Rapid advancement propelled by high-performance computation, global collaboration, and cross-disciplinary integration.\n\n"
            f"### 3. Core Application Domains & Real-World Use Cases\n"
            f"- **Enterprise & Industrial Optimization**: Accelerating workflows, automating critical operational pipelines, and enhancing resource efficiency.\n"
            f"- **Scientific & Medical Advancements**: Facilitating high-throughput discovery, predictive modeling, and diagnostic precision.\n"
            f"- **Public Infrastructure & Sustainability**: Enhancing resilience, resource allocation, and predictive environmental stewardship.\n"
            f"- **Next-Generation Consumer Solutions**: Driving adaptive services, accessibility, and high-performance communication systems.\n\n"
            f"### 4. Technical Architectures & Underlying Operational Principles\n"
            f"- **Foundational Layer**: High-integrity data acquisition, sensor systems, or domain-specific baseline inputs.\n"
            f"- **Analytical & Processing Engine**: Mathematical modeling, algorithmic transformation, and state optimization pipelines.\n"
            f"- **Execution & Feedback Loop**: Dynamic monitoring, error mitigation, and closed-loop performance stabilization.\n\n"
            f"### 5. Technical Constraints, Bottlenecks & Open Inquiries\n"
            f"- Scalability limits under rigorous real-time constraints and complex non-linear environments.\n"
            f"- Standardization gaps, governance challenges, and interpretability requirements.\n"
            f"- Resource intensity (computational, financial, or thermodynamic) during continuous scaling.\n\n"
            f"### 6. Primary Sources & Grounded References\n"
            f"{refs_text}"
        )

    def _dynamic_analysis_output(self, ctx: Dict[str, Any], prompt: str) -> str:
        topic = ctx["clean_topic"]
        return (
            f"### Analytical Synthesis & Strategic Impact Breakdown for {topic}\n\n"
            f"#### A. Value Drivers & Transformative Shifts\n"
            f"1. **Paradigm Shift in Efficiency**: {topic} moves the paradigm from incremental heuristic iteration "
            f"to systemic, data-driven optimization, unlocking substantial operational dividends.\n"
            f"2. **Cross-Sector Convergence**: Solutions pioneered in {topic} cross-pollinate adjacent disciplines, "
            f"accelerating discoveries across engineering, biology, and computational sciences.\n"
            f"3. **Capital & Knowledge Acceleration**: Substantial institutional and private capital inflows are compressing "
            f"the time required from primary research to market-ready implementation.\n\n"
            f"#### B. Multi-Industry Comparative Impact Matrix\n"
            f"- **High Urgency & High Impact**: Direct mission-critical operations where precision and uptime are non-negotiable.\n"
            f"- **High Adoption Maturity**: Structured environments where standardized data pipelines exist and ROI is quantifiable.\n"
            f"- **High Regulatory & Structural Friction**: Sectors constrained by legacy infrastructure, compliance hurdles, and liability mandates.\n\n"
            f"#### C. Vulnerabilities, Systemic Bottlenecks & Strategic Trade-offs\n"
            f"- **Infrastructure Dependencies**: Reliance on specialized tooling, capital-intensive equipment, or proprietary ecosystems.\n"
            f"- **Risk of Premature Scaling**: Deploying models before edge-case vulnerabilities and failure modes are comprehensively verified.\n"
            f"- **Talent & Knowledge Asymmetry**: High barriers to entry concentrated among a limited cohort of specialized institutions."
        )

    def _dynamic_verification_output(self, ctx: Dict[str, Any], prompt: str) -> str:
        topic = ctx["clean_topic"]
        refs = ctx["references"]
        ref_title = refs[0].get("title", topic) if refs else topic

        return (
            f"### Evidence Verification & Fact-Checking Audit for {topic}\n\n"
            f"#### 1. Claim Verification Scorecard\n"
            f"- [VERIFIED] **Domain Definition & Core Foundations**: Grounded against reference archives for *{ref_title}*.\n"
            f"- [VERIFIED] **Historical Milestone Progression**: Chronological evolution from theory to scaled application confirmed.\n"
            f"- [NUANCED] **Deployment Timelines & Readiness Levels**: While production adoption is accelerating, universal generalization remains contingent on addressing edge-case limitations.\n"
            f"- [UNSUPPORTED / SPECULATIVE] **Hypothetical Zero-Friction Scenarios**: Early claims downplaying implementation and compliance costs require realistic calibration.\n\n"
            f"#### 2. Identified Gaps & Missing Dimensions\n"
            f"- **Regulatory Frameworks & Standards**: Must emphasize international safety standards, compliance protocols, and liability.\n"
            f"- **Long-Term Sustainability**: Explicit assessment of thermodynamic, environmental, or economic sustainability is required.\n\n"
            f"#### 3. Directive Instructions for Writer Agent\n"
            f"- Frame {topic} objectively, balancing demonstrated breakthrough capabilities with tangible technological constraints.\n"
            f"- Ensure explicit incorporation of verified reference evidence and clear demarcations between current capabilities and future roadmap items."
        )

    def _dynamic_writer_output(self, ctx: Dict[str, Any], prompt: str) -> str:
        topic = ctx["clean_topic"]
        fact = ctx["primary_fact"] or f"{topic} is an advancing field of modern science, engineering, and practice."
        refs = ctx["references"]

        citations = ""
        if refs:
            for r in refs:
                citations += f"- [{r.get('title')}]({r.get('url')}): {r.get('summary')[:200]}...\n"
        else:
            citations = f"- [{topic} Knowledge Base](https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}): Technical literature and domain reviews.\n"

        return (
            f"# {topic}: Comprehensive Research & Application Report\n\n"
            f"**Multi-Agent Research Intelligence System | Powered by Sarvam AI**\n\n"
            f"**Agents Involved:** Research Agent, Analysis Agent, Verification Agent, Writer Agent\n\n"
            f"---\n\n"
            f"## Executive Summary\n"
            f"**{topic}** has emerged as a cornerstone of modern scientific, technological, and industrial progress. "
            f"{fact} "
            f"This comprehensive report integrates multi-agent factual discovery, strategic impact analysis, and empirical "
            f"verification audits to deliver an authoritative perspective on {topic}, its applications, and its future trajectory.\n\n"
            f"## 1. Introduction & Conceptual Foundations\n"
            f"The study of {topic} is rooted in the convergence of theoretical frameworks and empirical experimentation. "
            f"Historically developing from initial exploratory proofs to scalable enterprise methodologies, {topic} provides "
            f"the analytical and operational machinery necessary to model, optimize, and resolve complex systemic challenges.\n\n"
            f"## 2. Core Technological Architecture & How It Works\n"
            f"Operational implementations of {topic} typically function across three interconnected tiers:\n"
            f"1. **Input & Grounding Layer**: High-fidelity collection of domain signals, empirical metrics, and structured datasets.\n"
            f"2. **Processing & Optimization Core**: Algorithmic and computational routines that transform raw inputs into actionable insights, state estimations, or predictive models.\n"
            f"3. **Execution & Feedback Loop**: Closed-loop evaluation ensuring continuous accuracy, stability, and safety margins.\n\n"
            f"## 3. Comprehensive Breakdown of Applications (By Sector)\n"
            f"### A. Industry & Enterprise Infrastructure\n"
            f"- Automated operations and high-throughput process optimization reducing latency and overhead.\n"
            f"- Predictive diagnostics and predictive maintenance preventing costly systemic downtime.\n\n"
            f"### B. Science, Healthcare & Advanced Discovery\n"
            f"- Accelerating simulation fidelity, laboratory automation, and empirical hypothesis testing.\n"
            f"- Enhanced pattern recognition enabling earlier diagnostic insights and precision interventions.\n\n"
            f"### C. Public Systems & Sustainability\n"
            f"- Smart allocation of natural and energy resources through continuous real-time telemetry.\n"
            f"- Resilient infrastructure monitoring mitigating risks from unexpected systemic shocks.\n\n"
            f"## 4. Strategic Analysis, Challenges & Governance Considerations\n"
            f"While {topic} delivers significant leverage, several foundational challenges require deliberate stewardship:\n"
            f"- **Complexity & Edge-Case Management**: Ensuring robustness when encountering rare, high-stakes boundary conditions.\n"
            f"- **Economic & Resource Efficiency**: Balancing the capital and energy expenditure of scaling against realized returns.\n"
            f"- **Ethical Standards & Regulatory Alignment**: Adhering to evolving compliance frameworks to protect data integrity, safety, and accountability.\n\n"
            f"## 5. Multi-Agent Verification & Evidence Audit Trail\n"
            f"- Factual claims cross-referenced and verified against authoritative reference repositories.\n"
            f"- Potential exaggerations regarding near-term deployment horizons calibrated to reflect validated technical readiness levels.\n"
            f"- Comprehensive inclusion of regulatory, environmental, and structural dimensions mandated by the Verification Agent.\n\n"
            f"## 6. Strategic Recommendations & Future Outlook\n"
            f"Organizations pursuing {topic} should adopt a staged, modular implementation strategy: "
            f"prioritize robust data baselines, establish continuous verification and auditing layers, and foster "
            f"cross-disciplinary expertise to maximize strategic impact.\n\n"
            f"## 7. Citations & References\n"
            f"{citations}"
        )
