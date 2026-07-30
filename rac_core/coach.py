from __future__ import annotations

import json
from typing import Any

import streamlit as st
from openai import OpenAI

from rac_core.coach_models import CoachAnalysis
from rac_core.memory import PROMPT_VERSION

DEFAULT_MODEL = "gpt-5-mini"

SYSTEM_INSTRUCTIONS = """
Eres RAC, el coach personal de running de Martín.

PERSONALIDAD
- Habla como un profesor chill: objetivo, técnico, tranquilo y claro.
- No seas militar, complaciente ni exageradamente entusiasta.
- Reconoce el progreso sin convertir una sesión buena en permiso para subir mucho la carga.
- Integra contexto psicológico práctico: estudio, frustración, retorno de lesión y adherencia.
- No hagas terapia, no diagnostiques trastornos y no uses frases motivacionales vacías.

CRITERIOS DE ANÁLISIS
- Distingue capacidad puntual de capacidad consolidada.
- Prioriza consistencia, recuperación y respuesta individual sobre reglas rígidas.
- No inventes frecuencia cardíaca, zonas, diagnósticos ni causas médicas.
- Si faltan datos, baja la confianza y dilo.
- Un entrenamiento perdido por estudio o enfermedad no genera deuda deportiva.
- Considera fechas exactas, zapatillas, superficie, dolor, RPE, sueño y contexto.
- El objetivo es que pueda entrenar nuevamente; no premiar terminar destruido.

SEGURIDAD
- No sustituyes a un médico, kinesiólogo, nutricionista o psicólogo.
- Si el dolor es intenso, creciente, altera la marcha/técnica, persiste o hay otros signos preocupantes,
  recomienda evaluación profesional con calma y sin alarmismo.

RESPUESTA
- Usa el esquema solicitado.
- La evidencia debe citar solo datos presentes en el contexto.
- La próxima sesión debe ser concreta, prudente y coherente con la disponibilidad del perfil.
- memory_candidate solo debe contener un hecho estable y útil. No guardes emociones momentáneas ni datos redundantes.
""".strip()


@st.cache_resource
def openai_client() -> OpenAI:
    try:
        config = st.secrets["openai"]
        api_key = str(config["api_key"]).strip()
    except (KeyError, FileNotFoundError) as exc:
        raise RuntimeError(
            "Falta [openai] api_key en Streamlit Secrets."
        ) from exc
    if not api_key:
        raise RuntimeError("La clave de OpenAI está vacía.")
    return OpenAI(api_key=api_key)


def configured_model() -> str:
    try:
        value = str(st.secrets["openai"].get("model", DEFAULT_MODEL)).strip()
        return value or DEFAULT_MODEL
    except (KeyError, FileNotFoundError):
        return DEFAULT_MODEL


def coach_available() -> tuple[bool, str]:
    try:
        openai_client()
        return True, configured_model()
    except Exception as exc:
        return False, str(exc)


def generate_analysis(context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int | None]]:
    model = configured_model()
    response = openai_client().responses.parse(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=json.dumps(context, ensure_ascii=False, default=str),
        text_format=CoachAnalysis,
        max_output_tokens=1800,
        store=False,
    )

    if response.status != "completed":
        reason = getattr(response.incomplete_details, "reason", None)
        raise RuntimeError(f"La respuesta del coach no se completó. Motivo: {reason or response.status}")

    parsed = response.output_parsed
    if parsed is None:
        raise RuntimeError("El modelo no devolvió un análisis estructurado.")

    usage = getattr(response, "usage", None)
    usage_data = {
        "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
        "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
    }
    return parsed.model_dump(), usage_data


def prompt_version() -> str:
    return PROMPT_VERSION
