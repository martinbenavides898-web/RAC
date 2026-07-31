from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


TOKENS = {
    "bg": "#07050D",
    "bg_secondary": "#0D0914",
    "surface": "#16131D",
    "surface_elevated": "#201A29",
    "orange": "#FF5E14",
    "orange_hover": "#FF7133",
    "crimson": "#FF2A55",
    "cyan": "#24C7E8",
    "green": "#35D07F",
    "text": "#F4F6F8",
    "muted": "#8A99A8",
}


def apply_global_theme() -> None:
    """Aplica el sistema visual global sin modificar la lógica de RAC."""
    st.markdown(
        """
<style>
:root {
    --rac-bg: #07050D;
    --rac-bg-secondary: #0D0914;
    --rac-surface: #16131D;
    --rac-surface-elevated: #201A29;
    --rac-orange: #FF5E14;
    --rac-orange-hover: #FF7133;
    --rac-crimson: #FF2A55;
    --rac-cyan: #24C7E8;
    --rac-green: #35D07F;
    --rac-text: #F4F6F8;
    --rac-muted: #8A99A8;
    --rac-border: rgba(255, 255, 255, 0.08);
    --rac-shadow: 0 18px 44px rgba(0, 0, 0, 0.28);
    --rac-radius-lg: 22px;
    --rac-radius-md: 18px;
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

html, body {
    background: var(--rac-bg);
}

.stApp {
    color: var(--rac-text);
    background:
        radial-gradient(circle at 84% 8%, rgba(90, 38, 125, 0.17), transparent 36%),
        radial-gradient(circle at 7% 84%, rgba(66, 28, 95, 0.11), transparent 40%),
        linear-gradient(160deg, #07050D 0%, #0D0914 55%, #050407 100%);
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stAppViewContainer"] > .main {
    overflow-x: hidden;
}

.block-container {
    width: min(100%, 620px);
    max-width: 620px;
    padding: max(1.4rem, env(safe-area-inset-top)) 1rem 3rem;
    margin: 0 auto;
}

h1, h2, h3, h4, p, label {
    color: var(--rac-text);
}

/* Sidebar: una sola navegación, grande y coherente. */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 72% 0%, rgba(90, 38, 125, 0.15), transparent 31%),
        #0D0A12;
    border-right: 1px solid var(--rac-border);
}

[data-testid="stSidebarNav"]::before {
    content: "RAC";
    display: block;
    padding: 1.15rem 1rem 1.35rem;
    color: var(--rac-orange);
    font-size: 3.65rem;
    line-height: 0.82;
    font-weight: 950;
    font-style: italic;
    letter-spacing: -0.09em;
    text-shadow: 0 0 26px rgba(255, 94, 20, 0.16);
}

[data-testid="stSidebarNav"] a {
    min-height: 52px;
    margin: 0.15rem 0.45rem;
    padding: 0.65rem 0.8rem;
    border-radius: 13px;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.045);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(255, 94, 20, 0.16), rgba(255, 94, 20, 0.05));
    box-shadow: inset 3px 0 0 var(--rac-orange);
}

[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: var(--rac-text) !important;
    font-size: 1.08rem !important;
    font-weight: 680 !important;
}

[data-testid="stSidebarNav"] [data-testid="stNavSectionHeader"] {
    margin: 1.05rem 0.8rem 0.35rem;
    color: var(--rac-muted) !important;
    font-size: 0.9rem !important;
    font-weight: 750 !important;
    letter-spacing: 0.02em;
}

.rac-sidebar-meta {
    margin: 1.25rem 0.7rem 0;
    padding: 1.25rem 0.3rem 0.6rem;
    border-top: 1px solid var(--rac-border);
}

.rac-sidebar-footer-logo {
    margin-bottom: 0.7rem;
    color: var(--rac-orange);
    font-size: 2.15rem;
    line-height: 1;
    font-weight: 950;
    font-style: italic;
    letter-spacing: -0.08em;
}

.rac-sidebar-version {
    margin-bottom: 0.85rem;
    color: var(--rac-muted);
    font-size: 0.8rem;
    line-height: 1.45;
}

.rac-sidebar-status {
    padding: 0.9rem;
    color: #BFE9CF;
    font-size: 0.86rem;
    line-height: 1.5;
    border: 1px solid rgba(53, 208, 127, 0.18);
    border-radius: 14px;
    background: rgba(53, 208, 127, 0.1);
}

/* Formularios y páginas existentes. */
div[data-testid="stMetric"] {
    padding: 1rem;
    border: 1px solid var(--rac-border);
    border-radius: var(--rac-radius-md);
    background: linear-gradient(145deg, rgba(32, 26, 41, 0.94), rgba(22, 19, 29, 0.95));
    box-shadow: var(--rac-shadow);
}

div[data-testid="stForm"],
div[data-testid="stExpander"],
[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--rac-border);
    border-radius: var(--rac-radius-md);
    background: rgba(22, 19, 29, 0.92);
}

.stButton > button,
.stDownloadButton > button {
    min-height: 56px;
    border: 1px solid var(--rac-border);
    border-radius: 17px;
    font-weight: 780;
    transition: transform 140ms ease, background-color 140ms ease, box-shadow 140ms ease;
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform: scale(0.985);
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    color: #120906;
    background: linear-gradient(180deg, var(--rac-orange-hover), var(--rac-orange));
    border-color: rgba(255, 113, 51, 0.7);
    box-shadow: 0 10px 28px rgba(255, 94, 20, 0.2);
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
div[data-baseweb="select"] > div {
    color: var(--rac-text) !important;
    background: rgba(32, 26, 41, 0.94) !important;
    border-color: var(--rac-border) !important;
    border-radius: 14px !important;
}

/* Pantalla Hoy. */
.rac-home-header {
    margin-bottom: 1rem;
}

.rac-wordmark {
    margin-bottom: 1.15rem;
    color: var(--rac-orange);
    font-size: 1.45rem;
    line-height: 1;
    font-weight: 950;
    font-style: italic;
    letter-spacing: -0.08em;
}

.rac-greeting {
    margin: 0;
    color: var(--rac-text);
    font-size: clamp(1.9rem, 7vw, 2.45rem);
    line-height: 1.03;
    letter-spacing: -0.05em;
    font-weight: 830;
}

.rac-date {
    margin-top: 0.55rem;
    color: var(--rac-muted);
    font-size: 0.76rem;
    font-weight: 760;
    letter-spacing: 0.075em;
    text-transform: uppercase;
}

.rac-daily-readiness {
    margin: 1.1rem 0 0;
    color: #CDD3DA;
    font-size: 1.04rem;
    line-height: 1.48;
}

.rac-status-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.7rem;
    margin: 0.25rem 0 1rem;
}

.rac-status-card {
    min-width: 0;
    padding: 0.9rem 0.78rem 0.8rem;
    border: 1px solid var(--rac-border);
    border-radius: 17px;
    background: linear-gradient(150deg, rgba(32, 26, 41, 0.94), rgba(22, 19, 29, 0.94));
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.21);
}

.rac-status-head {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-width: 0;
}

.rac-status-dot {
    width: 8px;
    height: 8px;
    flex: 0 0 8px;
    border-radius: 50%;
    background: var(--status-color);
}

.rac-status-label {
    overflow: hidden;
    color: var(--rac-muted);
    font-size: 0.64rem;
    line-height: 1;
    font-weight: 820;
    letter-spacing: 0.065em;
    text-overflow: ellipsis;
    text-transform: uppercase;
    white-space: nowrap;
}

.rac-status-value {
    margin-top: 0.58rem;
    overflow: hidden;
    color: var(--rac-text);
    font-size: clamp(0.92rem, 3.2vw, 1.08rem);
    line-height: 1.15;
    font-weight: 760;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rac-status-track {
    height: 4px;
    margin-top: 0.72rem;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.09);
}

.rac-status-track span {
    display: block;
    width: var(--status-progress);
    height: 100%;
    border-radius: inherit;
    background: var(--status-color);
}

.st-key-rac_workout_section {
    padding: 1.15rem;
    border: 1px solid rgba(255, 94, 20, 0.68);
    border-radius: var(--rac-radius-lg);
    background:
        radial-gradient(circle at 100% 0%, rgba(255, 94, 20, 0.08), transparent 34%),
        linear-gradient(145deg, rgba(24, 21, 31, 0.98), rgba(13, 9, 20, 0.98));
    box-shadow: 0 16px 48px rgba(255, 94, 20, 0.1), var(--rac-shadow);
}

.st-key-rac_workout_section .stButton {
    margin-top: 1rem;
}

.st-key-rac_workout_section .stButton > button {
    width: 100%;
}

.rac-workout-eyebrow {
    color: var(--rac-orange);
    font-size: 0.8rem;
    font-weight: 850;
    letter-spacing: 0.045em;
    text-transform: uppercase;
}

.rac-workout-duration {
    margin: 0.82rem 0 0.2rem;
    color: var(--rac-text);
    font-size: clamp(3.3rem, 15vw, 4.5rem);
    line-height: 0.9;
    font-weight: 920;
    letter-spacing: -0.08em;
}

.rac-workout-duration span {
    margin-left: 0.22rem;
    font-size: 0.44em;
    letter-spacing: -0.035em;
}

.rac-workout-zone {
    color: #CBD1D8;
    font-size: 1rem;
}

.rac-workout-copy {
    margin: 0.78rem 0 0;
    color: #C0C8D0;
    font-size: 0.95rem;
    line-height: 1.5;
}

.st-key-rac_explanation {
    margin-top: 0.9rem;
}

.st-key-rac_explanation [data-testid="stExpander"] {
    box-shadow: var(--rac-shadow);
}

.rac-weekly-card {
    margin-top: 0.9rem;
    padding: 1rem;
    border: 1px solid var(--rac-border);
    border-radius: var(--rac-radius-md);
    background: linear-gradient(145deg, rgba(32, 26, 41, 0.84), rgba(22, 19, 29, 0.9));
    box-shadow: var(--rac-shadow);
}

.rac-weekly-title {
    margin-bottom: 0.9rem;
    color: var(--rac-muted);
    font-size: 0.76rem;
    font-weight: 820;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

.rac-weekly-metrics {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.7rem;
}

.rac-weekly-value {
    color: var(--rac-text);
    font-size: clamp(1rem, 4vw, 1.22rem);
    line-height: 1.1;
    font-weight: 820;
    white-space: nowrap;
}

.rac-weekly-label {
    margin-top: 0.25rem;
    color: var(--rac-muted);
    font-size: 0.59rem;
    font-weight: 760;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.rac-week-strip {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.4rem;
    margin-top: 1rem;
}

.rac-week-day {
    color: var(--rac-muted);
    font-size: 0.6rem;
    font-weight: 770;
    text-align: center;
}

.rac-week-day::before {
    content: "";
    display: block;
    height: 4px;
    margin-bottom: 0.42rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.1);
}

.rac-week-day.is-trained::before {
    background: var(--rac-orange);
}

.rac-week-day.is-today {
    color: var(--rac-text);
}

@media (max-width: 430px) {
    .block-container {
        padding-right: 0.78rem;
        padding-left: 0.78rem;
    }

    .rac-status-grid {
        gap: 0.48rem;
    }

    .rac-status-card {
        padding-right: 0.58rem;
        padding-left: 0.58rem;
    }

    .rac-weekly-metrics {
        gap: 0.45rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def status_card_html(*, label: str, value: str, color: str, progress: int) -> str:
    safe_progress = max(0, min(100, int(progress)))
    return (
        f'<div class="rac-status-card" style="--status-color:{escape(color)};--status-progress:{safe_progress}%">'
        f'<div class="rac-status-head"><span class="rac-status-dot"></span>'
        f'<span class="rac-status-label">{escape(label)}</span></div>'
        f'<div class="rac-status-value">{escape(value)}</div>'
        '<div class="rac-status-track"><span></span></div>'
        '</div>'
    )


def render_status_grid(cards: Iterable[dict[str, object]]) -> None:
    """Renderiza las tarjetas como HTML real, sin pasar por el parser Markdown."""
    cards_html = "".join(status_card_html(**card) for card in cards)
    st.html(f'<div class="rac-status-grid">{cards_html}</div>')
