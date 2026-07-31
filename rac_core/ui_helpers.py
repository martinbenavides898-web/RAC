import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def persistence_status() -> None:
    st.success("RAC está conectado a Supabase. Los registros tienen persistencia entre reinicios.")


def local_storage_warning() -> None:
    """Backward-compatible name retained for pages from RAC v0.1."""
    persistence_status()
