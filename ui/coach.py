from __future__ import annotations

from datetime import date

import streamlit as st

from rac_core.coach import coach_available, configured_model, generate_analysis, prompt_version
from rac_core.db import (
    add_memory,
    get_activities,
    get_analysis_by_hash,
    get_usage_totals,
    save_analysis,
)
from rac_core.memory import build_context, context_hash, context_size
from rac_core.metrics import pace_text, week_bounds
from rac_core.ui_helpers import page_header

page_header("Coach IA", "Análisis con memoria propia, contexto compacto y respuestas reutilizables.")

available, detail = coach_available()
if not available:
    st.warning("El coach todavía no tiene una clave de Gemini configurada.")
    st.code(
        '[gemini]\napi_key = "PEGA_AQUI_TU_CLAVE"\nmodel = "gemini-3.1-flash-lite"',
        language="toml",
    )
    st.caption(detail)
    st.caption("La clave se crea gratis en Google AI Studio. No la subas a GitHub ni la pegues en el chat.")
    st.stop()

usage = get_usage_totals()
c1, c2, c3 = st.columns(3)
c1.metric("Modelo Gemini", configured_model())
c2.metric("Análisis guardados", usage["calls"])
c3.metric("Tokens procesados", f'{usage["input_tokens"] + usage["output_tokens"]:,}')


def render_analysis(result: dict, *, cache_label: str = "") -> None:
    if cache_label:
        st.caption(cache_label)
    st.markdown(f'### {result["verdict"]}')
    for item in result["evidence"]:
        st.write(f"- {item}")

    left, right = st.columns(2)
    left.markdown("#### Lectura física")
    left.write(result["physical_interpretation"])
    right.markdown("#### Contexto psicológico")
    right.write(result["psychological_context"])

    c1, c2 = st.columns(2)
    c1.metric("Riesgo", result["risk_level"].capitalize())
    c2.metric("Confianza", result["confidence"].capitalize())

    st.markdown("#### Próxima acción")
    st.write(result["next_action"])
    st.info(f'**Próxima sesión:** {result["next_session"]}')

    if result.get("warning"):
        st.warning(result["warning"])
    if result.get("professional_attention"):
        st.error("RAC recomienda evaluación profesional antes de progresar la carga.")

    candidate = result.get("memory_candidate")
    if candidate:
        with st.expander("Posible memoria nueva"):
            st.write(candidate)
            title = st.text_input("Título para esta memoria", value="Aprendizaje del coach")
            if st.button("Guardar como memoria", key=f"memory_{hash(candidate)}"):
                add_memory(
                    {
                        "category": "Decisión",
                        "title": title,
                        "content": candidate,
                        "importance": 3,
                        "source": "coach IA confirmado por usuario",
                    }
                )
                st.success("Memoria guardada.")


def run_or_load(
    *,
    analysis_type: str,
    reference_key: str,
    context: dict,
    request_text: str = "",
    activity_id: int | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    force: bool = False,
) -> tuple[dict, str]:
    input_hash = context_hash(context)
    existing = None if force else get_analysis_by_hash(input_hash)
    if existing:
        return existing["response_json"], "Análisis reutilizado: no se hizo una llamada nueva a la API."

    result, usage_data = generate_analysis(context)
    save_analysis(
        {
            "analysis_type": analysis_type,
            "reference_key": reference_key,
            "input_hash": input_hash,
            "request_text": request_text,
            "activity_id": activity_id,
            "period_start": period_start,
            "period_end": period_end,
            "response_json": result,
            "model": configured_model(),
            "prompt_version": prompt_version(),
            **usage_data,
        }
    )
    return result, f"Análisis nuevo · contexto compacto de {context_size(context):,} caracteres."


run_tab, week_tab, ask_tab = st.tabs(["🏃 Último entrenamiento", "📊 Semana", "💬 Preguntar"])

with run_tab:
    activities = get_activities(descending=True, limit=20)
    if not activities:
        st.info("Registra un entrenamiento antes de pedir un análisis.")
    else:
        selected_id = st.selectbox(
            "Entrenamiento",
            [a["id"] for a in activities],
            format_func=lambda activity_id: next(
                f'{a["activity_date"]} · {a["distance_km"]:.1f} km · {pace_text(a["distance_km"], a["duration_min"])}'
                for a in activities
                if a["id"] == activity_id
            ),
        )
        activity = next(a for a in activities if a["id"] == selected_id)
        force = st.checkbox("Regenerar aunque ya exista", key="force_run")
        if st.button("Analizar entrenamiento", type="primary", use_container_width=True):
            context = build_context(task="Analizar entrenamiento", target_activity=activity)
            with st.spinner("RAC está revisando datos, contexto y memoria..."):
                try:
                    result, label = run_or_load(
                        analysis_type="entrenamiento",
                        reference_key=f"activity:{selected_id}",
                        context=context,
                        activity_id=int(selected_id),
                        force=force,
                    )
                    st.session_state["coach_result_run"] = (result, label)
                except Exception as exc:
                    st.error(f"No se pudo generar el análisis: {exc}")
        if "coach_result_run" in st.session_state:
            result, label = st.session_state["coach_result_run"]
            render_analysis(result, cache_label=label)

with week_tab:
    period = st.radio("Periodo", ["Semana actual", "Semana pasada"], horizontal=True)
    start, end = week_bounds(date.today(), previous=period == "Semana pasada")
    st.write(f"**{start.strftime('%d-%m-%Y')} al {end.strftime('%d-%m-%Y')}**")
    force = st.checkbox("Regenerar aunque ya exista", key="force_week")
    if st.button("Generar reporte IA", type="primary", use_container_width=True):
        context = build_context(
            task="Evaluar semana deportiva",
            period_start=start.isoformat(),
            period_end=end.isoformat(),
        )
        with st.spinner("RAC está preparando el reporte semanal..."):
            try:
                result, label = run_or_load(
                    analysis_type="semana",
                    reference_key=f"week:{start.isoformat()}:{end.isoformat()}",
                    context=context,
                    period_start=start.isoformat(),
                    period_end=end.isoformat(),
                    force=force,
                )
                st.session_state["coach_result_week"] = (result, label)
            except Exception as exc:
                st.error(f"No se pudo generar el reporte: {exc}")
    if "coach_result_week" in st.session_state:
        result, label = st.session_state["coach_result_week"]
        render_analysis(result, cache_label=label)

with ask_tab:
    question = st.text_area(
        "Pregunta para RAC",
        placeholder="Ej.: ¿Conviene que el sábado aumente el fondo o consolide la distancia?",
    )
    st.caption("RAC recibe tu perfil, memorias activas y los últimos 14 días; no recibe un chat infinito.")
    if st.button("Preguntar al coach", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Escribe una pregunta.")
        else:
            context = build_context(task="Responder pregunta del corredor", question=question)
            with st.spinner("RAC está revisando tu contexto..."):
                try:
                    result, label = run_or_load(
                        analysis_type="pregunta",
                        reference_key=f"question:{context_hash(context)[:12]}",
                        context=context,
                        request_text=question.strip(),
                    )
                    st.session_state["coach_result_question"] = (result, label)
                except Exception as exc:
                    st.error(f"No se pudo responder: {exc}")
    if "coach_result_question" in st.session_state:
        result, label = st.session_state["coach_result_question"]
        render_analysis(result, cache_label=label)
