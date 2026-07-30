import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def local_storage_warning() -> None:
    st.warning(
        "RAC v0.1 usa SQLite local. En Streamlit Community Cloud estos archivos no tienen "
        "persistencia garantizada. Usa la página Respaldo mientras conectamos la base definitiva.",
        icon="⚠️",
    )
