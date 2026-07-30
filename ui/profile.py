import json

import streamlit as st

from rac_core.db import get_profile, set_profile_value
from rac_core.ui_helpers import page_header

page_header("Perfil RAC", "Esta es la memoria estable que el futuro coach recibirá.")

profile = get_profile()

coach_style = st.text_area("Estilo del coach", value=profile.get("coach_style", ""))
primary_goal = st.text_area("Objetivo principal", value=profile.get("primary_goal", ""))
endurance_goal = st.text_area("Objetivo de resistencia", value=profile.get("endurance_goal", ""))
pace_goal = st.text_area("Objetivo de ritmo", value=profile.get("pace_goal", ""))
coach_rule = st.text_area("Regla principal del coach", value=profile.get("coach_rule", ""))

if st.button("Guardar perfil", type="primary"):
    set_profile_value("coach_style", coach_style.strip())
    set_profile_value("primary_goal", primary_goal.strip())
    set_profile_value("endurance_goal", endurance_goal.strip())
    set_profile_value("pace_goal", pace_goal.strip())
    set_profile_value("coach_rule", coach_rule.strip())
    st.success("Perfil guardado.")

with st.expander("Ver memoria estructurada"):
    st.json(get_profile())
