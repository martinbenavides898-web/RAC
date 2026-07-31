import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def persistence_status() -> None:
    st.success(
        "RAC está conectado a Supabase. Los registros tienen persistencia entre reinicios.",
        icon="☁️",
    )


def local_storage_warning() -> None:
    """Backward-compatible name retained for pages from RAC v0.1."""
    persistence_status()


def bottom_navigation(*, active: str = "today") -> None:
    """Mobile-first navigation that complements Streamlit's preserved sidebar navigation."""
    with st.container(key="rac_bottom_nav"):
        columns = st.columns(4)
        items = [
            ("today", "ui/dashboard.py", "Hoy", "🔥"),
            ("train", "ui/register_run.py", "Entrenar", "🏃"),
            ("progress", "ui/weekly_report.py", "Progreso", "📊"),
            ("coach", "ui/coach.py", "Coach", "🤖"),
        ]
        for column, (item_id, page, label, icon) in zip(columns, items):
            with column:
                with st.container(key=f"rac_nav_{item_id}" if item_id == active else f"rac_nav_item_{item_id}"):
                    st.page_link(page, label=label, icon=icon)
