# 🧠 AI Research Assistant with Sarvam AI (Multi-Agent System)

An enterprise-grade, modular **Multi-Agent Research Assistant** built with Python and powered by **Sarvam AI** foundation models (such as `sarvam-105b`).

The system demonstrates the fundamental concepts of multi-agent systems—specialized agent roles, task decomposition, inter-agent data passing, fact-checking verification loops, and centralized workflow orchestration.

---

## 🏛️ Multi-Agent Architecture & Workflow

```text
            USER
              │
              ▼
       COORDINATOR AGENT
              │
       Assigns the tasks
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
 RESEARCH AGENT   ANALYSIS AGENT
      │               │
      └───────┬───────┘
              │
              ▼
       VERIFICATION AGENT
              │
              ▼
         WRITER AGENT
              │
              ▼
        FINAL REPORT
```

---

## 👥 The Agents and Their Responsibilities

| Agent | Name | Role & Responsibility |
| :--- | :--- | :--- |
| **0** | **Coordinator Agent** | Manages the workflow state, assigns tasks sequentially, routes intermediate artifacts, tracks execution timing, and saves the final dossier. |
| **1** | **Research Agent** | Gathers factual background knowledge from web/Wikipedia tools and Sarvam AI, structures definitions, historical milestones, and use cases. |
| **2** | **Analysis Agent** | Reads the research results, identifies underlying patterns, analyzes multi-sector business impact, and surfaces technical trade-offs. |
| **3** | **Verification Agent** | Audits claims against evidence, detects missing context or hyperbole, creates a verification scorecard (`[VERIFIED]`, `[CAVEAT]`, `[UNSUPPORTED]`), and issues editorial directives. |
| **4** | **Writer Agent** | Synthesizes verified findings, analytical insights, and verification corrections into an authoritative, publication-grade Executive Research Report. |

---

## 🚀 Key Features

- **Sarvam AI Integration**: Seamless communication with Sarvam AI's Chat Completion APIs (`https://api.sarvam.ai/v1/chat/completions`) supporting models like `sarvam-105b`.
- **Knowledge Retrieval**: Built-in Wikipedia REST tool providing factual grounding before generation.
- **Verification & Audit Loop**: An explicit verification agent prevents hallucinations and ensures balanced coverage.
- **Interactive Web UI**: Modern Streamlit dashboard (`app.py`) with real-time agent status indicators and tabs to inspect intermediate findings.
- **Rich Terminal CLI**: Terminal interface (`main.py`) with colored progress bars, tables, and formatted markdown rendering.
- **Offline Demo / Simulation Mode**: Test the complete multi-agent pipeline immediately even before setting an API key.

---

## 📂 Project Structure

```text
Research_agent/
│
├── .env.example               # Template for Sarvam AI credentials
├── requirements.txt           # Project dependencies
├── README.md                  # System documentation
├── config.py                  # Environment and configuration loader
├── sarvam_client.py           # Sarvam AI REST API client & offline simulator
│
├── tools/
│   ├── __init__.py
│   └── search_tool.py         # Knowledge retriever (Wikipedia & open web API)
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # BaseAgent abstraction & AgentResult data model
│   ├── research_agent.py      # Agent 1: Research Agent
│   ├── analysis_agent.py      # Agent 2: Analysis Agent
│   ├── verification_agent.py  # Agent 3: Verification Agent
│   ├── writer_agent.py        # Agent 4: Writer Agent
│   └── coordinator.py         # Coordinator Agent (Workflow Orchestrator)
│
├── main.py                    # Terminal CLI with Rich visualization
├── app.py                     # Interactive Streamlit Web Dashboard
├── test_agents.py             # Automated unit and integration test suite
└── reports/                   # Output directory for generated markdown reports
```

---

## ⚙️ Setup & Installation

### 1. Clone or Open the Workspace
```bash
cd c:\Users\11dee\OneDrive\Desktop\Research_agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your Sarvam AI API Key
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and insert your Sarvam AI API key:
```env
SARVAM_API_KEY=your_actual_sarvam_api_key_here
SARVAM_MODEL=sarvam-105b
SARVAM_BASE_URL=https://api.sarvam.ai/v1
SARVAM_TEMPERATURE=0.2
DEMO_MODE=False
```

> **Note:** If you don't have an API key yet, the system automatically runs in **Demo / Simulation Mode**, allowing you to explore the full workflow immediately!

---

## 💻 How to Run

### Option A: Launch Interactive Streamlit Web UI
```bash
streamlit run app.py
```
This opens a modern dashboard in your browser (`http://localhost:8501`) where you can:
- Enter research queries
- Adjust temperature and models
- Watch each agent transition through `Waiting` ➔ `Active` ➔ `Completed`
- Inspect intermediate agent outputs and download final markdown reports.

---

### Option B: Run via Terminal CLI
Run with the default prompt:
```bash
python main.py
```

Run with a custom topic:
```bash
python main.py --topic "Research Artificial Intelligence and explain its applications."
```

Run in interactive prompt mode:
```bash
python main.py -i
```

Run explicitly in demo/offline mode:
```bash
python main.py --demo
```

---

### Option C: Run Automated Tests
Verify all 4 agents, the retriever tool, and the coordinator:
```bash
python test_agents.py
```

---

## 📑 Example Output Workflow

When user enters:
> *"Research Artificial Intelligence and explain its applications."*

1. **Coordinator** receives the request and initializes pipeline state.
2. **Research Agent** gathers historical milestones (Turing 1950, Dartmouth 1956, Transformers 2017) and applications across healthcare, finance, and engineering.
3. **Analysis Agent** extracts value drivers (cognitive task automation, high-leverage sectors, compute centralization bottlenecks).
4. **Verification Agent** audits claims, verifies historical milestones, flags autonomous driving caveats, and demands ethical/governance inclusions.
5. **Writer Agent** compiles the authoritative executive report with an executive summary, industry breakdowns, and a verification audit trail.
6. **Coordinator** outputs the report and saves the complete dossier to `reports/`.
