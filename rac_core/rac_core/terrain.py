from __future__ import annotations

import hashlib
from typing import Any

import gpxpy


def analyze_gpx_bytes(gpx_bytes: bytes) -> dict[str, Any]:
    """
    Analiza un archivo GPX real y extrae distancia, desnivel positivo/negativo,
    y desglose kilómetro a kilómetro (pendientes, falsos llanos, subidas y bajadas).
    """
    file_sha256 = hashlib.sha256(gpx_bytes).hexdigest()
    gpx = gpxpy.parse(gpx_bytes.decode("utf-8", errors="replace"))

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                points.append(pt)

    if len(points) < 2:
        raise ValueError("El archivo GPX no contiene suficientes puntos de trazado.")

    total_distance_m = 0.0
    total_gain_m = 0.0
    total_loss_m = 0.0
    elevations = [p.elevation for p in points if p.elevation is not None]

    km_buckets: list[dict[str, Any]] = []
    current_km = 1
    km_start_ele = points[0].elevation or 0.0
    km_gain = 0.0
    km_loss = 0.0

    for i in range(1, len(points)):
        prev_pt = points[i - 1]
        curr_pt = points[i]
        dist = curr_pt.distance_2d(prev_pt) or 0.0
        total_distance_m += dist

        if prev_pt.elevation is not None and curr_pt.elevation is not None:
            diff = curr_pt.elevation - prev_pt.elevation
            if diff > 0:
                total_gain_m += diff
                km_gain += diff
            elif diff < 0:
                total_loss_m += abs(diff)
                km_loss += abs(diff)

        if total_distance_m >= current_km * 1000:
            curr_ele = curr_pt.elevation or km_start_ele
            net_ele = curr_ele - km_start_ele
            grade_pct = (net_ele / 1000.0) * 100.0

            if grade_pct >= 2.0:
                terrain_tag = "Subida exigente"
            elif 0.6 <= grade_pct < 2.0:
                terrain_tag = "Falso llano de subida"
            elif -0.6 < grade_pct < 0.6:
                terrain_tag = "Llano"
            elif -2.0 < grade_pct <= -0.6:
                terrain_tag = "Falso llano de bajada"
            else:
                terrain_tag = "Bajada rápida (alto impacto excéntrico)"

            km_buckets.append(
                {
                    "km": current_km,
                    "net_elevation_m": round(net_ele, 1),
                    "gain_m": round(km_gain, 1),
                    "loss_m": round(km_loss, 1),
                    "grade_pct": round(grade_pct, 2),
                    "classification": terrain_tag,
                }
            )
            current_km += 1
            km_start_ele = curr_ele
            km_gain = 0.0
            km_loss = 0.0

    return {
        "file_sha256": file_sha256,
        "total_distance_km": round(total_distance_m / 1000.0, 3),
        "elevation_gain_m": round(total_gain_m, 1),
        "elevation_loss_m": round(total_loss_m, 1),
        "min_altitude_m": round(min(elevations), 1) if elevations else None,
        "max_altitude_m": round(max(elevations), 1) if elevations else None,
        "segments": km_buckets,
    }
