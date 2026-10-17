from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CoachAnalysis(BaseModel):
    verdict: str = Field(description="Conclusión central breve y objetiva.")
    evidence: list[str] = Field(
        min_length=1,
        max_length=5,
        description="Datos concretos que sostienen el análisis.",
    )
    physical_interpretation: str
    psychological_context: str
    risk_level: Literal["bajo", "moderado", "alto", "datos insuficientes"]
    confidence: Literal["baja", "media", "alta"]
    next_action: str
    next_session: str
    warning: str | None = None
    professional_attention: bool = False
    memory_candidate: str | None = Field(
        default=None,
        description="Hecho estable potencialmente útil para el futuro. Nulo si no corresponde.",
    )
