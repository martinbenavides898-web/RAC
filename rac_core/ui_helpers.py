import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def local_storage_warning() -> None:
    st.success(
        "RAC está conectado a Supabase. Los registros ya tienen persistencia entre reinicios.",
        icon="☁️",
    )
