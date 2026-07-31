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
    """Apply RAC's global visual tokens without changing application logic."""
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
            --rac-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
            --rac-radius-lg: 22px;
            --rac-radius-md: 18px;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "SF Pro Display",
                "Segoe UI", sans-serif;
        }

        html, body {
            background: var(--rac-bg);
        }

        .stApp {
            color: var(--rac-text);
            background:
                radial-gradient(circle at 82% 8%, rgba(90, 38, 125, 0.18), transparent 36%),
                radial-gradient(circle at 8% 82%, rgba(66, 28, 95, 0.12), transparent 40%),
                linear-gradient(160deg, #07050D 0%, #0D0914 55%, #050407 100%);
            background-attachment: fixed;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            right: 0.55rem;
        }

        [data-testid="stAppViewContainer"] > .main {
            overflow-x: hidden;
        }

        .block-container {
            width: min(100%, 520px);
            max-width: 520px;
            padding: max(1.15rem, env(safe-area-inset-top)) 1rem
                calc(7.4rem + env(safe-area-inset-bottom));
            margin: 0 auto;
        }

        h1, h2, h3, h4, p {
            color: var(--rac-text);
        }

        h1 {
            font-size: clamp(1.8rem, 7vw, 2.25rem) !important;
            letter-spacing: -0.045em;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 70% 0%, rgba(90, 38, 125, 0.16), transparent 30%),
                #0D0A12;
            border-right: 1px solid var(--rac-border);
        }

        [data-testid="stSidebar"] a,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: var(--rac-text);
        }

        [data-testid="stSidebarNav"]::before {
            content: "RAC";
            display: block;
            padding: 0.7rem 1rem 1rem;
            color: var(--rac-orange);
            font-size: 3rem;
            line-height: 0.9;
            font-weight: 950;
            font-style: italic;
            letter-spacing: -0.09em;
            text-shadow: 0 0 24px rgba(255, 94, 20, 0.18);
        }

        [data-testid="stSidebarNav"] a {
            min-height: 48px;
            border-radius: 12px;
        }

        [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebarNav"] a p {
            font-size: 1.02rem !important;
            font-weight: 650 !important;
        }

        [data-testid="stSidebarNav"] [data-testid="stNavSectionHeader"] {
            margin-top: 0.85rem;
            font-size: 0.82rem !important;
            letter-spacing: 0.035em;
        }

        .rac-sidebar-meta {
            margin-top: 1.1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--rac-border);
        }

        .rac-sidebar-footer-logo {
            margin-bottom: 0.8rem;
            color: var(--rac-orange);
            font-size: 2rem;
            line-height: 1;
            font-weight: 950;
            font-style: italic;
            letter-spacing: -0.08em;
        }

        .rac-sidebar-version {
            margin-bottom: 0.8rem;
            color: var(--rac-muted);
            font-size: 0.78rem;
            line-height: 1.45;
        }

        .rac-sidebar-status {
            padding: 0.95rem;
            color: #BFE9CF;
            font-size: 0.86rem;
            line-height: 1.55;
            border: 1px solid rgba(53, 208, 127, 0.18);
            border-radius: 14px;
            background: rgba(53, 208, 127, 0.11);
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(32, 26, 41, 0.94), rgba(22, 19, 29, 0.95));
            border: 1px solid var(--rac-border);
            border-radius: var(--rac-radius-md);
            padding: 1rem;
            box-shadow: var(--rac-shadow);
        }

        div[data-testid="stForm"],
        div[data-testid="stExpander"],
        [data-testid="stDataFrame"] {
            border: 1px solid var(--rac-border);
            border-radius: var(--rac-radius-md);
            background: rgba(22, 19, 29, 0.92);
            overflow: hidden;
        }

        div[data-testid="stExpander"] details {
            border: none;
        }

        .stButton > button,
        .stDownloadButton > button {
            min-height: 54px;
            border-radius: 17px;
            border: 1px solid var(--rac-border);
            font-weight: 750;
            transition: transform 150ms ease, background-color 150ms ease,
                box-shadow 150ms ease;
        }

        .stButton > button:active,
        .stDownloadButton > button:active {
            transform: scale(0.985);
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            color: #130B08;
            background: linear-gradient(180deg, var(--rac-orange-hover), var(--rac-orange));
            border-color: rgba(255, 113, 51, 0.72);
            box-shadow: 0 10px 30px rgba(255, 94, 20, 0.2);
        }

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {
            color: #080505;
            background: var(--rac-orange-hover);
            border-color: var(--rac-orange-hover);
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

        .rac-app-shell {
            width: 100%;
        }

        .rac-topbar {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.8rem;
        }

        .rac-wordmark {
            color: var(--rac-orange);
            font-size: 1.35rem;
            line-height: 1;
            font-weight: 950;
            font-style: italic;
            letter-spacing: -0.08em;
            margin-bottom: 1.15rem;
        }

        .rac-greeting {
            margin: 0;
            color: var(--rac-text);
            font-size: clamp(1.72rem, 7.4vw, 2.1rem);
            line-height: 1.04;
            letter-spacing: -0.045em;
            font-weight: 780;
        }

        .rac-date {
            margin-top: 0.45rem;
            color: var(--rac-muted);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.075em;
            text-transform: uppercase;
        }

        .rac-bell {
            position: relative;
            width: 44px;
            height: 44px;
            flex: 0 0 44px;
            display: grid;
            place-items: center;
            color: var(--rac-text);
            border: 1px solid var(--rac-border);
            border-radius: 15px;
            background: rgba(22, 19, 29, 0.72);
            box-shadow: var(--rac-shadow);
        }

        .rac-bell svg {
            width: 21px;
            height: 21px;
            fill: none;
            stroke: currentColor;
            stroke-width: 1.8;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .rac-bell::after {
            content: "";
            position: absolute;
            top: 8px;
            right: 8px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--rac-orange);
            border: 2px solid var(--rac-bg-secondary);
        }

        .rac-daily-readiness {
            max-width: 31rem;
            margin: 0 0 1rem;
            color: #C7CED6;
            font-size: 1.05rem;
            line-height: 1.45;
        }

        .rac-status-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0 0 0.9rem;
        }

        .rac-status-card {
            min-width: 0;
            padding: 0.82rem 0.72rem 0.72rem;
            border: 1px solid var(--rac-border);
            border-radius: 16px;
            background: linear-gradient(150deg, rgba(32, 26, 41, 0.92), rgba(22, 19, 29, 0.92));
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.22);
        }

        .rac-status-top {
            display: flex;
            align-items: center;
            gap: 0.38rem;
            min-width: 0;
        }

        .rac-status-dot {
            width: 8px;
            height: 8px;
            flex: 0 0 8px;
            border-radius: 50%;
            background: var(--rac-status-color);
            box-shadow: 0 0 12px color-mix(in srgb, var(--rac-status-color) 58%, transparent);
        }

        .rac-status-label {
            overflow: hidden;
            color: var(--rac-muted);
            font-size: 0.61rem;
            line-height: 1;
            font-weight: 800;
            letter-spacing: 0.07em;
            text-overflow: ellipsis;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .rac-status-value {
            margin-top: 0.55rem;
            overflow: hidden;
            color: var(--rac-text);
            font-size: clamp(0.86rem, 3.3vw, 1rem);
            line-height: 1.15;
            font-weight: 720;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .rac-status-track {
            height: 3px;
            margin-top: 0.7rem;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.09);
        }

        .rac-status-track span {
            display: block;
            width: var(--rac-status-progress, 70%);
            height: 100%;
            border-radius: inherit;
            background: var(--rac-status-color, var(--rac-orange));
            box-shadow: 0 0 14px color-mix(in srgb, var(--rac-status-color) 52%, transparent);
        }

        .rac-workout-card {
            position: relative;
            padding: 1.15rem;
            overflow: hidden;
            border: 1px solid rgba(255, 94, 20, 0.72);
            border-radius: var(--rac-radius-lg);
            background:
                radial-gradient(circle at 100% 0%, rgba(255, 94, 20, 0.08), transparent 34%),
                linear-gradient(145deg, rgba(24, 21, 31, 0.98), rgba(13, 9, 20, 0.98));
            box-shadow: 0 16px 50px rgba(255, 94, 20, 0.11), var(--rac-shadow);
        }

        .rac-workout-eyebrow {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--rac-orange);
            font-size: 0.79rem;
            font-weight: 850;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .rac-run-mark {
            position: relative;
            display: inline-block;
            width: 18px;
            height: 14px;
            flex: 0 0 18px;
        }

        .rac-run-mark::before,
        .rac-run-mark::after {
            content: "";
            position: absolute;
            height: 2px;
            border-radius: 999px;
            background: var(--rac-orange);
            transform-origin: left center;
        }

        .rac-run-mark::before {
            top: 4px;
            left: 2px;
            width: 14px;
            transform: rotate(-22deg);
        }

        .rac-run-mark::after {
            top: 10px;
            left: 5px;
            width: 11px;
            transform: rotate(24deg);
        }

        .rac-workout-duration {
            margin: 0.8rem 0 0.15rem;
            color: var(--rac-text);
            font-size: clamp(3rem, 16vw, 4.1rem);
            line-height: 0.9;
            font-weight: 900;
            letter-spacing: -0.075em;
        }

        .rac-workout-duration span {
            margin-left: 0.2rem;
            font-size: 0.46em;
            letter-spacing: -0.04em;
        }

        .rac-workout-zone {
            margin-top: 0.55rem;
            color: #C7CED6;
            font-size: 1rem;
        }

        .rac-workout-copy {
            margin: 0.75rem 0 0;
            color: #C1C8D0;
            font-size: 0.94rem;
            line-height: 1.52;
        }

        .st-key-rac_primary_action {
            margin-top: -0.1rem;
            padding: 0 1.15rem 1.15rem;
            border-right: 1px solid rgba(255, 94, 20, 0.72);
            border-bottom: 1px solid rgba(255, 94, 20, 0.72);
            border-left: 1px solid rgba(255, 94, 20, 0.72);
            border-radius: 0 0 var(--rac-radius-lg) var(--rac-radius-lg);
            background: linear-gradient(145deg, rgba(24, 21, 31, 0.98), rgba(13, 9, 20, 0.98));
            box-shadow: 0 16px 50px rgba(255, 94, 20, 0.11);
        }

        .st-key-rac_primary_action .stButton > button {
            width: 100%;
            color: #120906;
            background: linear-gradient(180deg, var(--rac-orange-hover), var(--rac-orange));
            border: 0;
            box-shadow: 0 12px 28px rgba(255, 94, 20, 0.24);
        }

        .rac-coach-note,
        .rac-weekly-card {
            margin-top: 0.8rem;
            padding: 1rem;
            border: 1px solid var(--rac-border);
            border-radius: var(--rac-radius-md);
            background: linear-gradient(145deg, rgba(32, 26, 41, 0.82), rgba(22, 19, 29, 0.88));
            box-shadow: var(--rac-shadow);
        }

        .rac-coach-note summary {
            cursor: pointer;
            color: var(--rac-text);
            font-size: 0.98rem;
            font-weight: 720;
            list-style: none;
        }

        .rac-coach-note summary::-webkit-details-marker {
            display: none;
        }

        .rac-coach-note summary::after {
            content: "⌄";
            float: right;
            color: var(--rac-muted);
        }

        .rac-coach-note[open] summary::after {
            transform: rotate(180deg);
        }

        .rac-coach-note p {
            margin: 0.75rem 0 0;
            color: #BCC5CF;
            font-size: 0.91rem;
            line-height: 1.52;
        }

        .rac-weekly-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.85rem;
            color: var(--rac-muted);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.075em;
            text-transform: uppercase;
        }

        .rac-weekly-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 0.75rem;
        }

        .rac-weekly-metric {
            min-width: 0;
        }

        .rac-weekly-value {
            color: var(--rac-text);
            font-size: clamp(1.03rem, 4.2vw, 1.25rem);
            line-height: 1.1;
            font-weight: 800;
            white-space: nowrap;
        }

        .rac-weekly-label {
            margin-top: 0.24rem;
            color: var(--rac-muted);
            font-size: 0.58rem;
            font-weight: 750;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .rac-week-strip {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.38rem;
            margin-top: 1rem;
        }

        .rac-week-day {
            text-align: center;
            color: var(--rac-muted);
            font-size: 0.58rem;
            font-weight: 760;
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
            box-shadow: 0 0 12px rgba(255, 94, 20, 0.35);
        }

        .rac-week-day.is-today {
            color: var(--rac-text);
        }

        .st-key-rac_bottom_nav {
            position: fixed;
            z-index: 50;
            right: 50%;
            bottom: max(0.7rem, env(safe-area-inset-bottom));
            width: min(calc(100% - 1.25rem), 500px);
            padding: 0.4rem 0.5rem;
            transform: translateX(50%);
            border: 1px solid var(--rac-border);
            border-radius: 22px;
            background: rgba(13, 9, 20, 0.9);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.42);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .st-key-rac_bottom_nav [data-testid="stHorizontalBlock"] {
            gap: 0.25rem;
        }

        .st-key-rac_bottom_nav [data-testid="stPageLink"] a {
            min-height: 50px;
            justify-content: center;
            gap: 0.15rem;
            padding: 0.35rem 0.2rem;
            color: var(--rac-muted);
            border-radius: 15px;
            font-size: 0.72rem;
            font-weight: 730;
            text-align: center;
        }

        .st-key-rac_bottom_nav [data-testid="stPageLink"] a:hover {
            color: var(--rac-text);
            background: rgba(255, 255, 255, 0.045);
        }

        .st-key-rac_nav_today [data-testid="stPageLink"] a {
            color: var(--rac-orange) !important;
            background: rgba(255, 94, 20, 0.09);
        }

        @media (max-width: 390px) {
            .block-container {
                padding-right: 0.78rem;
                padding-left: 0.78rem;
            }

            .rac-status-grid {
                gap: 0.45rem;
            }

            .rac-status-card {
                padding-right: 0.55rem;
                padding-left: 0.55rem;
            }

            .rac-weekly-metrics {
                gap: 0.45rem;
            }
        }

        @media (min-width: 760px) {
            .block-container {
                padding-top: 2rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                transition: none !important;
                animation: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_card_html(
    *,
    label: str,
    value: str,
    color: str,
    progress: int,
) -> str:
    safe_progress = max(0, min(100, int(progress)))
    return f"""
    <div class="rac-status-card" style="--rac-status-color:{escape(color)};--rac-status-progress:{safe_progress}%">
        <div class="rac-status-top">
            <span class="rac-status-dot" aria-hidden="true"></span>
            <span class="rac-status-label">{escape(label)}</span>
        </div>
        <div class="rac-status-value">{escape(value)}</div>
        <div class="rac-status-track"><span></span></div>
    </div>
    """


def render_status_grid(cards: Iterable[dict[str, object]]) -> None:
    html = "".join(status_card_html(**card) for card in cards)
    st.markdown(f'<div class="rac-status-grid">{html}</div>', unsafe_allow_html=True)
