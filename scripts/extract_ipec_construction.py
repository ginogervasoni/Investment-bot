#!/usr/bin/env python3
"""Descarga y normaliza las series oficiales de construcción de IPEC.

Genera data/construction-series.json con datos de Gran Santa Fe (costos) y
Santa Fe Capital (superficie autorizada). No distribuye cifras municipales
entre vecinales porque la fuente no publica ese nivel geográfico.
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "construction-series.json"
TMP = ROOT / ".data-cache"

FALLBACK_URLS = {
    "cost_variations": "https://www.estadisticasantafe.gob.ar/wp-content/uploads/sites/24/2026/09/Variaciones-nivel-general-y-capitulos.-Enero-2022-julio-2026-2.xlsx",
    "cost_values": "https://www.estadisticasantafe.gob.ar/wp-content/uploads/sites/24/2026/09/Valor-total-m2-y-por-capitulos.-Enero-2022-julio-2026-1.xlsx",
    "permits": "https://www.estadisticasantafe.gob.ar/wp-content/uploads/sites/24/2026/05/Permisos-de-Edificacion-en-m2-por-municipio.-Ene-2010-a-jul-2026-.xlsx",
}
PAGES = {
    "cost": "https://www.estadisticasantafe.gob.ar/contenido/costo-de-la-construccion-aglomerados-santa-fe-y-rosario/",
    "permits": "https://www.estadisticasantafe.gob.ar/contenido/permisos-de-edificacion-2/",
}

MONTHS = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


def download_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Nodo-Santa-Fe/1.0"})
    last_error = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except OSError as error:
            last_error = error
            if attempt < 3:
                time.sleep(2 ** attempt)
    raise last_error


def discover_workbook(page: str, keywords: tuple[str, ...], fallback: str) -> str:
    try:
        html = download_bytes(page).decode("utf-8", errors="ignore")
        links = [unescape(value) for value in re.findall(r'href=["\']([^"\']+\.xlsx[^"\']*)', html, re.I)]
        candidates = [urljoin(page, link) for link in links if all(word in link.lower() for word in keywords)]
        return sorted(candidates)[-1] if candidates else fallback
    except OSError:
        return fallback


def download(name: str, url: str) -> Path:
    TMP.mkdir(exist_ok=True)
    target = TMP / f"{name}.xlsx"
    target.write_bytes(download_bytes(url))
    return target


def write_if_changed(payload: dict) -> None:
    if OUT.exists():
        previous = json.loads(OUT.read_text(encoding="utf-8"))
        old_comparable = {key: value for key, value in previous.items() if key != "generated_at"}
        new_comparable = {key: value for key, value in payload.items() if key != "generated_at"}
        if old_comparable == new_comparable:
            print(f"Sin cambios oficiales: {OUT}")
            return
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Actualizado {OUT}")


def clean_month(value: object) -> str:
    return re.sub(r"\s|\*", "", str(value or ""))


def parse_costs(variations: Path, values: Path) -> list[dict]:
    var_ws = openpyxl.load_workbook(variations, data_only=True, read_only=True)["cc_vriaciones nivel gral. y cap"]
    val_ws = openpyxl.load_workbook(values, data_only=True, read_only=True)["cc valor m2  total y  capitulos"]

    def parse(ws, columns):
        year = None
        result = {}
        for row in ws.iter_rows(min_row=8, values_only=True):
            if isinstance(row[0], int):
                year = row[0]
            month = clean_month(row[1])
            if year and month in MONTHS and isinstance(row[2], (int, float)):
                period = f"{year}-{MONTHS[month]:02d}"
                result[period] = {key: row[index] for key, index in columns.items()}
        return result

    variation_rows = parse(var_ws, {"monthly_change_pct": 2, "materials_change_pct": 3, "labor_change_pct": 4, "overhead_change_pct": 5})
    value_rows = parse(val_ws, {"total_ars_m2": 2, "materials_ars_m2": 3, "labor_ars_m2": 4, "overhead_ars_m2": 5})
    periods = sorted(set(variation_rows) & set(value_rows))[-13:]
    return [{"period": period, **{k: round(v, 2) for k, v in value_rows[period].items()}, **{k: round(v, 2) for k, v in variation_rows[period].items()}} for period in periods]


def parse_permits(path: Path) -> list[dict]:
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True).active
    start = next(index for index, row in enumerate(ws.iter_rows(values_only=True), 1) if row[0] == "SANTA FE")
    records = []
    for row in ws.iter_rows(min_row=start + 1, max_row=start + 17, values_only=True):
        match = re.match(r"Año (\d{4})", str(row[0] or ""))
        if not match:
            continue
        year = int(match.group(1))
        for month_index, month_name in enumerate(list(MONTHS), start=2):
            value = row[month_index]
            if isinstance(value, (int, float)):
                records.append({"period": f"{year}-{MONTHS[month_name]:02d}", "authorized_m2": int(value)})
    return sorted(records, key=lambda item: item["period"])


def main() -> None:
    urls = {
        "cost_variations": discover_workbook(PAGES["cost"], ("variaciones", "nivel-general"), FALLBACK_URLS["cost_variations"]),
        "cost_values": discover_workbook(PAGES["cost"], ("valor-total", "m2"), FALLBACK_URLS["cost_values"]),
        "permits": discover_workbook(PAGES["permits"], ("permisos-de-edificacion", "municipio"), FALLBACK_URLS["permits"]),
    }
    files = {name: download(name, url) for name, url in urls.items()}
    costs = parse_costs(files["cost_variations"], files["cost_values"])
    permits = parse_permits(files["permits"])
    latest = costs[-1]
    year_ago = next(row for row in costs if row["period"] == f"{int(latest['period'][:4]) - 1}{latest['period'][4:]}")
    current_year = int(permits[-1]["period"][:4])
    current_ytd = sum(row["authorized_m2"] for row in permits if row["period"].startswith(str(current_year)))
    prior_ytd = sum(row["authorized_m2"] for row in permits if row["period"].startswith(str(current_year - 1)) and row["period"][5:] <= permits[-1]["period"][5:])

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "latest_period": latest["period"],
        "scope_note": "Costos: aglomerado Gran Santa Fe. Permisos: municipio Santa Fe. No son datos por vecinal.",
        "summary": {
            "cost_ars_m2": latest["total_ars_m2"],
            "cost_monthly_change_pct": latest["monthly_change_pct"],
            "cost_yoy_change_pct": round((latest["total_ars_m2"] / year_ago["total_ars_m2"] - 1) * 100, 2),
            "permits_ytd_m2": current_ytd,
            "permits_ytd_change_pct": round((current_ytd / prior_ytd - 1) * 100, 2),
            "permits_latest_month_m2": permits[-1]["authorized_m2"],
        },
        "cost_gran_santa_fe": costs,
        "permits_santa_fe_city": permits[-13:],
        "sources": [
            {"title": "Costo de la construcción aglomerados Santa Fe y Rosario", "publisher": "IPEC", "url": "https://www.estadisticasantafe.gob.ar/contenido/costo-de-la-construccion-aglomerados-santa-fe-y-rosario/", "status": "provisional_latest_months"},
            {"title": "Permisos de edificación", "publisher": "IPEC", "url": "https://www.estadisticasantafe.gob.ar/contenido/permisos-de-edificacion-2/", "status": "administrative_records"},
        ],
    }
    write_if_changed(payload)
    print(f"Fuentes procesadas: {len(costs)} costos, {len(permits)} permisos")


if __name__ == "__main__":
    main()
