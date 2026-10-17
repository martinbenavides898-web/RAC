import pandas as pd
import streamlit as st

from rac_core.db import add_memory, delete_memory, get_memories, set_memory_active
from rac_core.ui_helpers import page_header

page_header(
    "Memoria RAC",
    "RAC guarda hechos seleccionados, no una conversación infinita.",
)

memories = get_memories(active_only=False)
active_count = sum(1 for m in memories if m["active"])
characters = sum(len(m["content"]) for m in memories if m["active"])

c1, c2, c3 = st.columns(3)
c1.metric("Memorias activas", active_count)
c2.metric("Memorias totales", len(memories))
c3.metric("Texto activo", f"{characters:,} caracteres")

st.info(
    "Solo las memorias activas y el perfil compacto llegan al coach. "
    "Los análisis no agregan recuerdos automáticamente: tú decides qué conservar."
)

if memories:
    df = pd.DataFrame(
        [
            {
                "ID": m["id"],
                "Categoría": m["category"],
                "Título": m["title"],
                "Importancia": m["importance"],
                "Activa": "Sí" if m["active"] else "No",
                "Contenido": m["content"],
            }
            for m in memories
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)

st.subheader("Agregar memoria")
with st.form("memory_form"):
    category = st.selectbox(
        "Categoría",
        ["Preferencia", "Historial", "Lesión", "Objetivo", "Contexto", "Decisión"],
    )
    title = st.text_input("Título corto")
    content = st.text_area("Hecho que RAC debe recordar")
    importance = st.slider("Importancia", 1, 5, 3)
    submitted = st.form_submit_button("Guardar memoria", type="primary")

if submitted:
    if not title.strip() or not content.strip():
        st.error("El título y el contenido son obligatorios.")
    else:
        add_memory(
            {
                "category": category,
                "title": title,
                "content": content,
                "importance": importance,
                "source": "manual",
            }
        )
        st.success("Memoria guardada.")
        st.rerun()

if memories:
    st.subheader("Administrar")
    selected_id = st.selectbox(
        "Memoria",
        [m["id"] for m in memories],
        format_func=lambda memory_id: next(
            f'{m["title"]} · {"activa" if m["active"] else "inactiva"}'
            for m in memories
            if m["id"] == memory_id
        ),
    )
    selected = next(m for m in memories if m["id"] == selected_id)
    c1, c2 = st.columns(2)
    if c1.button("Desactivar" if selected["active"] else "Activar", use_container_width=True):
        set_memory_active(int(selected_id), not bool(selected["active"]))
        st.rerun()
    confirm = c2.checkbox("Confirmar eliminación")
    if c2.button("Eliminar", disabled=not confirm, use_container_width=True):
        delete_memory(int(selected_id))
        st.rerun()
