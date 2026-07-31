from __future__ import annotations

import json
from typing import Any

import streamlit as st
from google import genai
from google.genai import types

from rac_core.coach_models import CoachAnalysis
from rac_core.memory import PROMPT_VERSION

DEFAULT_MODEL = "gemini-2.5-flash-lite"

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
- Si el dolor es intenso, creciente, altera la marcha o la técnica, persiste o hay otros signos preocupantes,
  recomienda evaluación profesional con calma y sin alarmismo.

RESPUESTA
- Usa estrictamente el esquema solicitado.
- La evidencia debe citar solo datos presentes en el contexto.
- La próxima sesión debe ser concreta, prudente y coherente con la disponibilidad del perfil.
- memory_candidate solo debe contener un hecho estable y útil. No guardes emociones momentáneas ni datos redundantes.
""".strip()


@st.cache_resource
def gemini_client() -> genai.Client:
    """Crea un cliente de Gemini del lado del servidor usando Streamlit Secrets."""
    try:
        config = st.secrets["gemini"]
        api_key = str(config["api_key"]).strip()
    except (KeyError, FileNotFoundError) as exc:
        raise RuntimeError(
            "Falta [gemini] api_key en Streamlit Secrets."
        ) from exc

    if not api_key:
        raise RuntimeError("La clave de Gemini está vacía.")

    return genai.Client(api_key=api_key)


def configured_model() -> str:
    try:
        value = str(st.secrets["gemini"].get("model", DEFAULT_MODEL)).strip()
        return value or DEFAULT_MODEL
    except (KeyError, FileNotFoundError):
        return DEFAULT_MODEL


def coach_available() -> tuple[bool, str]:
    try:
        gemini_client()
        return True, configured_model()
    except Exception as exc:
        return False, str(exc)


def _parse_response(response: Any) -> CoachAnalysis:
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, CoachAnalysis):
        return parsed
    if isinstance(parsed, dict):
        return CoachAnalysis.model_validate(parsed)

    text = getattr(response, "text", None)
    if text:
        return CoachAnalysis.model_validate_json(text)

    prompt_feedback = getattr(response, "prompt_feedback", None)
    block_reason = getattr(prompt_feedback, "block_reason", None) if prompt_feedback else None
    if block_reason:
        raise RuntimeError(f"Gemini bloqueó la respuesta: {block_reason}")

    raise RuntimeError("Gemini no devolvió un análisis estructurado.")


def generate_analysis(context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int | None]]:
    model = configured_model()
    prompt = (
        "Analiza el siguiente contexto de RAC. No agregues datos que no estén presentes.\n\n"
        + json.dumps(context, ensure_ascii=False, default=str, separators=(",", ":"))
    )

    response = gemini_client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema=CoachAnalysis,
            max_output_tokens=1800,
        ),
    )

    parsed = _parse_response(response)
    usage = getattr(response, "usage_metadata", None)
    usage_data = {
        "input_tokens": getattr(usage, "prompt_token_count", None) if usage else None,
        "output_tokens": getattr(usage, "candidates_token_count", None) if usage else None,
    }
    return parsed.model_dump(), usage_data


def prompt_version() -> str:
    return PROMPT_VERSION
