import streamlit as st


def bottom_navigation(*, active: str = "today") -> None:
    """Text-only mobile navigation, isolated from legacy helpers to avoid stale imports."""
    with st.container(key="rac_bottom_nav"):
        columns = st.columns(4)
        items = [
            ("today", "ui/dashboard.py", "Hoy"),
            ("train", "ui/register_run.py", "Entrenar"),
            ("progress", "ui/weekly_report.py", "Progreso"),
            ("coach", "ui/coach.py", "Coach"),
        ]
        for column, (item_id, page, label) in zip(columns, items):
            with column:
                container_key = (
                    f"rac_nav_{item_id}" if item_id == active else f"rac_nav_item_{item_id}"
                )
                with st.container(key=container_key):
                    st.page_link(page, label=label)
