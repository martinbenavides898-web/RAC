import pandas as pd
import streamlit as st

from rac_core.db import add_shoe, get_shoes
from rac_core.ui_helpers import page_header

page_header("Zapatillas", "RAC registra uso, contexto y kilometraje acumulado.")

shoes = get_shoes(active_only=False)
if shoes:
    df = pd.DataFrame(
        [
            {
                "ID": s["id"],
                "Apodo": s["nickname"],
                "Marca": s["brand"],
                "Modelo": s["model"],
                "Uso": s["use_context"],
                "Kilometraje": round(float(s["total_km"]), 1),
                "Activa": "Sí" if s["active"] else "No",
            }
            for s in shoes
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)

st.subheader("Agregar zapatilla")
with st.form("shoe_form"):
    c1, c2 = st.columns(2)
    brand = c1.text_input("Marca")
    model = c2.text_input("Modelo")
    nickname = st.text_input("Apodo corto")
    use_context = st.text_input("Uso previsto", placeholder="Ej.: cinta, calle, fondos...")
    initial_km = st.number_input("Kilometraje previo", min_value=0.0, value=0.0, step=1.0)
    submitted = st.form_submit_button("Agregar", type="primary")

if submitted:
    if not brand.strip() or not model.strip() or not nickname.strip():
        st.error("Marca, modelo y apodo son obligatorios.")
    else:
        try:
            add_shoe(
                {
                    "brand": brand.strip(),
                    "model": model.strip(),
                    "nickname": nickname.strip(),
                    "use_context": use_context.strip(),
                    "initial_km": float(initial_km),
                    "active": True,
                }
            )
            st.success("Zapatilla agregada.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo agregar: {exc}")
