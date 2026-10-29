"""Streamlit Web UI for the Sarvam AI Multi-Agent Research Assistant.

Designed with an ultra-premium Vibra-Tactile-Morphic aesthetic:
Fusing deep tactile physical dimensionality (extruded bevels, recessed wells, debossed tactile switches)
with high-vibrancy chromatic glows, luminous neon accents, and interactive haptic visual feedback.
"""

import time
from pathlib import Path
import streamlit as st

from config import Config
from sarvam_client import SarvamClient
from agents.coordinator import CoordinatorAgent, WorkflowExecutionState

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant | Sarvam AI Multi-Agent System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Vibra-Tactile-Morphism Design System
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global Canvas: Deep Obsidian with Ambient Chromatic Radial Mesh */
    html, body, .stApp {
        background-color: #0b0f19 !important;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.18) 0%, transparent 45%),
            radial-gradient(circle at 85% 20%, rgba(236, 72, 153, 0.14) 0%, transparent 40%),
            radial-gradient(circle at 50% 80%, rgba(14, 165, 233, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 80% 85%, rgba(168, 85, 247, 0.15) 0%, transparent 45%) !important;
        background-attachment: fixed !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f1f5f9 !important;
    }

    /* Completely hide any Streamlit sidebar */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Main container max width & padding */
    .block-container {
        max-width: 1200px !important;
        padding-top: 2.2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Vibra-Tactile Header Instrument Console */
    .vibra-header-card {
        background: linear-gradient(135deg, rgba(26, 34, 56, 0.75) 0%, rgba(13, 19, 36, 0.92) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 26px;
        padding: 2.2rem 2.6rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 
            0 20px 45px -10px rgba(0, 0, 0, 0.75),
            0 0 35px -5px rgba(99, 102, 241, 0.22),
            inset 0 1.5px 1px 0 rgba(255, 255, 255, 0.2),
            inset 0 -2px 4px 0 rgba(0, 0, 0, 0.6);
        margin-bottom: 2.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1.2rem;
        position: relative;
        overflow: hidden;
    }

    .vibra-header-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #6366f1, #ec4899, #06b6d4, transparent);
    }

    .vibra-title {
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.85rem;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .vibra-title-accent {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .vibra-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 500;
        margin-top: 0.5rem;
        margin-bottom: 0;
        letter-spacing: -0.01em;
    }

    .vibra-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 1.1rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: rgba(99, 102, 241, 0.12);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.35);
        box-shadow: 
            0 0 20px rgba(99, 102, 241, 0.35),
            inset 0 1px 1px rgba(255, 255, 255, 0.2),
            inset 0 -1px 2px rgba(0, 0, 0, 0.5);
    }

    .vibra-badge-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 10px #10b981, 0 0 20px #10b981;
        animation: vibraBlink 2s infinite ease-in-out;
    }

    @keyframes vibraBlink {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* Label styling */
    label[data-testid="stWidgetLabel"] p {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: -0.01em !important;
    }

    /* Tactile Recessed Input Well */
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div {
        background-color: #0d1424 !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 
            inset 0 4px 12px rgba(0, 0, 0, 0.85),
            0 8px 20px rgba(0, 0, 0, 0.4) !important;
        padding: 8px 12px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[data-baseweb="textarea"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 
            inset 0 4px 14px rgba(0, 0, 0, 0.9),
            0 0 0 2px rgba(99, 102, 241, 0.4),
            0 0 30px rgba(99, 102, 241, 0.3) !important;
    }

    div[data-baseweb="textarea"] textarea {
        background: transparent !important;
        background-color: transparent !important;
        color: #f8fafc !important;
        font-size: 1.08rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }

    /* Vibra-Tactile Capacitive Primary Button */
    div[data-testid="stFormSubmitButton"] > button,
    div.stButton > button {
        background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.08rem !important;
        letter-spacing: 0.01em !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-top: 1.5px solid rgba(255, 255, 255, 0.6) !important;
        box-shadow: 
            0 12px 28px -4px rgba(79, 70, 229, 0.65),
            0 0 35px rgba(99, 102, 241, 0.4),
            inset 0 1.5px 2px rgba(255, 255, 255, 0.5),
            inset 0 -3px 4px rgba(0, 0, 0, 0.4) !important;
        padding: 0.95rem 2.2rem !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        position: relative !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover,
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(180deg, #7175f5 0%, #5850ec 100%) !important;
        box-shadow: 
            0 18px 36px -4px rgba(99, 102, 241, 0.8),
            0 0 45px rgba(236, 72, 153, 0.4),
            inset 0 2px 2px rgba(255, 255, 255, 0.6),
            inset 0 -3px 4px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stFormSubmitButton"] > button:active,
    div.stButton > button:active {
        transform: translateY(2px) !important;
        box-shadow: 
            0 4px 12px rgba(79, 70, 229, 0.4),
            inset 0 3px 6px rgba(0, 0, 0, 0.7),
            inset 0 -1px 2px rgba(255, 255, 255, 0.2) !important;
    }

    /* Vibra-Tactile 4-Agent Modules */
    .tactile-agent-card {
        background: linear-gradient(145deg, rgba(23, 31, 52, 0.75) 0%, rgba(13, 19, 34, 0.9) 100%);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 22px;
        padding: 1.5rem 1.4rem;
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 
            0 14px 30px -8px rgba(0, 0, 0, 0.65),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.15),
            inset 0 -2px 4px rgba(0, 0, 0, 0.5);
        transition: all 0.25s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .tactile-agent-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 
            0 20px 40px -8px rgba(0, 0, 0, 0.8),
            0 0 25px rgba(99, 102, 241, 0.25),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.25);
    }

    /* Active Haptic Pulsing State */
    .tactile-agent-card.running {
        border-color: rgba(236, 72, 153, 0.6);
        box-shadow: 
            0 0 35px rgba(236, 72, 153, 0.4),
            0 0 20px rgba(99, 102, 241, 0.4),
            inset 0 0 15px rgba(236, 72, 153, 0.25),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.4);
        animation: hapticGlow 1.8s infinite alternate ease-in-out;
    }

    @keyframes hapticGlow {
        0% {
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.35), inset 0 0 10px rgba(99, 102, 241, 0.2);
        }
        100% {
            border-color: rgba(236, 72, 153, 0.7);
            box-shadow: 0 0 40px rgba(236, 72, 153, 0.55), inset 0 0 18px rgba(236, 72, 153, 0.3);
        }
    }

    .tactile-step-label {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.4rem;
    }

    .agent-1-accent { color: #38bdf8; }
    .agent-2-accent { color: #c084fc; }
    .agent-3-accent { color: #fbbf24; }
    .agent-4-accent { color: #34d399; }

    .tactile-agent-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.25rem;
        letter-spacing: -0.01em;
    }

    .tactile-agent-desc {
        font-size: 0.83rem;
        color: #94a3b8;
        line-height: 1.35;
        margin-bottom: 1.1rem;
    }

    /* Tactile Status Badges */
    .pill-tactile-idle {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        background: #080c14;
        color: #64748b;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6);
    }

    .pill-tactile-running {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.95rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 800;
        background: rgba(236, 72, 153, 0.2);
        color: #f472b6;
        border: 1px solid #ec4899;
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.3);
    }

    .pill-tactile-done {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.95rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 800;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.5);
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.25);
    }

    /* Vibra Neon Progress Bar */
    div[data-testid="stProgress"] > div {
        background-color: #080c14 !important;
        border-radius: 999px !important;
        box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.8) !important;
        padding: 3px !important;
        height: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899, #06b6d4) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.8), 0 0 30px rgba(236, 72, 153, 0.6) !important;
        animation: progressFlow 3s linear infinite;
    }

    /* Tactile Dock Tabs */
    div[data-baseweb="tab-list"] {
        background: #080c14 !important;
        padding: 7px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 
            inset 0 3px 8px rgba(0, 0, 0, 0.8),
            0 10px 25px rgba(0, 0, 0, 0.4) !important;
        gap: 6px !important;
        margin-bottom: 1.8rem !important;
    }

    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 14px !important;
        padding: 9px 20px !important;
        border: 1px solid transparent !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 
            0 6px 18px rgba(0, 0, 0, 0.6),
            0 0 20px rgba(99, 102, 241, 0.4),
            inset 0 1px 1px rgba(255, 255, 255, 0.25) !important;
    }

    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Vibra-Tactile Document Canvas */
    div[data-testid="stTabContent"] > div {
        background: linear-gradient(135deg, rgba(20, 27, 45, 0.75) 0%, rgba(11, 16, 30, 0.92) 100%) !important;
        backdrop-filter: blur(24px) !important;
        border-radius: 26px !important;
        padding: 2.8rem 3rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
        box-shadow: 
            0 24px 50px -10px rgba(0, 0, 0, 0.8),
            0 0 40px -10px rgba(99, 102, 241, 0.2),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.18),
            inset 0 -2px 4px rgba(0, 0, 0, 0.6) !important;
        line-height: 1.8 !important;
    }

    div[data-testid="stTabContent"] h1 {
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 1.2rem !important;
    }

    div[data-testid="stTabContent"] h2 {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #818cf8 !important;
        margin-top: 2rem !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding-bottom: 0.4rem !important;
    }

    div[data-testid="stTabContent"] h3 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #f472b6 !important;
        margin-top: 1.5rem !important;
    }

    div[data-testid="stTabContent"] p, 
    div[data-testid="stTabContent"] li {
        color: #cbd5e1 !important;
        font-size: 1.05rem !important;
    }

    div[data-testid="stTabContent"] strong {
        color: #ffffff !important;
    }

    div[data-testid="stTabContent"] a {
        color: #38bdf8 !important;
        text-decoration: none !important;
        border-bottom: 1px dotted #38bdf8 !important;
    }

    div[data-testid="stTabContent"] a:hover {
        color: #7dd3fc !important;
        border-bottom: 1px solid #7dd3fc !important;
    }

    /* Vibra-Tactile Download Action Button */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-top: 1.5px solid rgba(255, 255, 255, 0.6) !important;
        box-shadow: 
            0 10px 24px -4px rgba(16, 185, 129, 0.6),
            0 0 30px rgba(16, 185, 129, 0.35),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.4),
            inset 0 -2px 3px rgba(0, 0, 0, 0.4) !important;
        padding: 0.8rem 1.8rem !important;
        transition: all 0.18s ease !important;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 
            0 16px 32px -4px rgba(16, 185, 129, 0.8),
            0 0 40px rgba(52, 211, 153, 0.45) !important;
    }

    /* Vibra Alert Box */
    div[data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        border: 1px solid rgba(16, 185, 129, 0.5) !important;
        border-radius: 20px !important;
        box-shadow: 
            0 14px 30px rgba(0, 0, 0, 0.6),
            0 0 25px rgba(16, 185, 129, 0.25),
            inset 0 1px 1px rgba(255, 255, 255, 0.2) !important;
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }

    /* Metric Slate Cards */
    .tactile-metric-card {
        background: linear-gradient(145deg, rgba(26, 34, 56, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-radius: 20px;
        padding: 1.6rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 
            0 14px 28px rgba(0, 0, 0, 0.6),
            inset 0 1.5px 1px rgba(255, 255, 255, 0.15),
            inset 0 -2px 4px rgba(0, 0, 0, 0.5);
        text-align: center;
    }

    .tactile-metric-label {
        color: #94a3b8;
        font-size: 0.88rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }

    .tactile-metric-value {
        font-size: 2.1rem;
        font-weight: 900;
        letter-spacing: -0.02em;
    }

    /* Table in Metrics */
    div[data-testid="stTable"] table {
        background: #0d1322 !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
        color: #e2e8f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_tactile_agent_card(placeholder, step_num: int, name: str, role: str, accent_class: str, status: str = "idle", duration: float = 0.0):
    """Renders a single Vibra-Tactile Agent Card with tactile bevels and luminous states."""
    if status == "idle":
        pill = '<span class="pill-tactile-idle">Waiting</span>'
        card_class = "tactile-agent-card"
    elif status == "running":
        pill = '<span class="pill-tactile-running">Active ⚡</span>'
        card_class = "tactile-agent-card running"
    else:
        pill = f'<span class="pill-tactile-done">✓ Done ({duration}s)</span>'
        card_class = "tactile-agent-card"

    html = f"""
    <div class="{card_class}">
        <div class="tactile-step-label {accent_class}">Agent {step_num}</div>
        <div class="tactile-agent-title">{name}</div>
        <div class="tactile-agent-desc">{role}</div>
        <div>{pill}</div>
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)


def main():
    # Load configuration in the background
    api_key = Config.SARVAM_API_KEY
    model = Config.SARVAM_MODEL
    demo_mode = Config.DEMO_MODE or not Config.has_api_key()

    # Vibra-Tactile Header Console
    mode_text = "SIMULATION ENGINE" if demo_mode else f"LIVE: {model.upper()}"
    st.markdown(
        f"""
        <div class="vibra-header-card">
            <div>
                <h1 class="vibra-title">
                    <span>⚡</span> AI Research Assistant <span class="vibra-title-accent">Multi-Agent</span>
                </h1>
                <p class="vibra-subtitle">
                    Autonomous 4-agent collaborative intelligence pipeline powered by Sarvam AI
                </p>
            </div>
            <div>
                <div class="vibra-badge">
                    <span class="vibra-badge-dot"></span>
                    <span>{mode_text}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tactile Query Input Form
    default_prompt = "Research Artificial Intelligence and explain its applications."
    with st.form("research_query_form", border=False):
        user_topic = st.text_area(
            "Enter your research query or instruction:",
            value=default_prompt,
            height=100,
            help="Type any research topic. The 4 agents will dynamically research, analyze, verify, and write an executive report.",
        )
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            start_btn = st.form_submit_button("🚀 Start Multi-Agent Research", use_container_width=True)

    # 4 Vibra-Tactile Agent Instruments
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card1 = st.empty()
        render_tactile_agent_card(card1, 1, "Research Agent", "Information Gathering", "agent-1-accent", "idle")
    with col2:
        card2 = st.empty()
        render_tactile_agent_card(card2, 2, "Analysis Agent", "Strategic Breakdown", "agent-2-accent", "idle")
    with col3:
        card3 = st.empty()
        render_tactile_agent_card(card3, 3, "Verification Agent", "Evidence & Audit", "agent-3-accent", "idle")
    with col4:
        card4 = st.empty()
        render_tactile_agent_card(card4, 4, "Writer Agent", "Final Synthesis", "agent-4-accent", "idle")

    # Workflow Execution
    if start_btn and user_topic.strip():
        progress_bar = st.progress(0)
        status_box = st.empty()

        # Instantiate Client & Coordinator
        client = SarvamClient(
            api_key=api_key,
            model=model,
            demo_mode=demo_mode,
        )
        coordinator = CoordinatorAgent(client=client)

        def on_step_start(name: str, role: str, step: int, total: int):
            status_box.markdown(f"⚡ **Pipeline Executing (Step {step}/{total}):** `{name}` actively processing...")
            progress_bar.progress((step - 1) / total)
            if step == 1:
                render_tactile_agent_card(card1, 1, "Research Agent", "Information Gathering", "agent-1-accent", "running")
            elif step == 2:
                render_tactile_agent_card(card2, 2, "Analysis Agent", "Strategic Breakdown", "agent-2-accent", "running")
            elif step == 3:
                render_tactile_agent_card(card3, 3, "Verification Agent", "Evidence & Audit", "agent-3-accent", "running")
            elif step == 4:
                render_tactile_agent_card(card4, 4, "Writer Agent", "Final Synthesis", "agent-4-accent", "running")

        def on_step_complete(res, step: int, total: int):
            progress_bar.progress(step / total)
            if step == 1:
                render_tactile_agent_card(card1, 1, "Research Agent", "Information Gathering", "agent-1-accent", "done", res.execution_time)
            elif step == 2:
                render_tactile_agent_card(card2, 2, "Analysis Agent", "Strategic Breakdown", "agent-2-accent", "done", res.execution_time)
            elif step == 3:
                render_tactile_agent_card(card3, 3, "Verification Agent", "Evidence & Audit", "agent-3-accent", "done", res.execution_time)
            elif step == 4:
                render_tactile_agent_card(card4, 4, "Writer Agent", "Final Synthesis", "agent-4-accent", "done", res.execution_time)

        with st.spinner("Multi-Agent Coordinator orchestrating workflow..."):
            exec_state: WorkflowExecutionState = coordinator.run_workflow(
                topic=user_topic.strip(),
                on_step_start=on_step_start,
                on_step_complete=on_step_complete,
            )

        progress_bar.progress(1.0)
        status_box.success(
            f"🎉 Multi-agent workflow completed successfully in {exec_state.total_duration}s!"
        )

        st.session_state["exec_state"] = exec_state
        st.session_state["executed"] = True

    # Render Vibra-Tactile Dossier Tabs
    if st.session_state.get("executed") and "exec_state" in st.session_state:
        exec_state: WorkflowExecutionState = st.session_state["exec_state"]

        st.markdown("<br>", unsafe_allow_html=True)
        tabs = st.tabs([
            "📄 Final Executive Report",
            "🔍 Agent 1: Research",
            "📊 Agent 2: Analysis",
            "🛡️ Agent 3: Verification",
            "⏱️ Execution Metrics",
        ])

        # Tab 1: Final Report
        with tabs[0]:
            st.markdown(exec_state.final_report)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Research Report (.md)",
                data=exec_state.final_report,
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
            )

        # Tab 2: Research Agent Findings
        with tabs[1]:
            res_r = exec_state.agent_results.get("research")
            if res_r:
                st.subheader(f"{res_r.agent_name} — {res_r.role}")
                st.caption(f"Execution: {res_r.execution_time}s | Engine: {res_r.metadata.get('model')}")
                sources = res_r.metadata.get("retrieved_sources", [])
                if sources:
                    st.markdown("**Grounded Reference Sources:**")
                    for s in sources:
                        st.markdown(f"- [{s.get('title')}]({s.get('url')}): {s.get('summary')[:220]}...")
                    st.markdown("---")
                st.markdown(res_r.output)

        # Tab 3: Analysis Agent Insights
        with tabs[2]:
            res_a = exec_state.agent_results.get("analysis")
            if res_a:
                st.subheader(f"{res_a.agent_name} — {res_a.role}")
                st.caption(f"Execution: {res_a.execution_time}s | Engine: {res_a.metadata.get('model')}")
                st.markdown(res_a.output)

        # Tab 4: Verification Agent Audit
        with tabs[3]:
            res_v = exec_state.agent_results.get("verification")
            if res_v:
                st.subheader(f"{res_v.agent_name} — {res_v.role}")
                st.caption(f"Execution: {res_v.execution_time}s | Engine: {res_v.metadata.get('model')}")
                st.markdown(res_v.output)

        # Tab 5: Metrics & Metadata
        with tabs[4]:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(
                    f'<div class="tactile-metric-card">'
                    f'<div class="tactile-metric-label">Total Duration</div>'
                    f'<div class="tactile-metric-value" style="color:#818cf8;">{exec_state.total_duration}s</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_m2:
                st.markdown(
                    f'<div class="tactile-metric-card">'
                    f'<div class="tactile-metric-label">Pipeline Units</div>'
                    f'<div class="tactile-metric-value" style="color:#34d399;">4 Agents</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_m3:
                st.markdown(
                    f'<div class="tactile-metric-card">'
                    f'<div class="tactile-metric-label">Workflow Status</div>'
                    f'<div class="tactile-metric-value" style="color:#f472b6;">{exec_state.status.upper()}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            table_rows = []
            for _, res in exec_state.agent_results.items():
                table_rows.append({
                    "Agent": res.agent_name,
                    "Role": res.role,
                    "Execution Time (s)": res.execution_time,
                    "Status": res.status.capitalize(),
                    "Engine": res.metadata.get("model", "N/A"),
                })
            st.table(table_rows)


if __name__ == "__main__":
    main()
