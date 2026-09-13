#!/usr/bin/env python3
"""Build the Step 6 affordability dataset from official INDEC and BCRA files."""

from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import xlrd

EPH_URL = "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_{period}_txt.zip"
BCRA_UVA_URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/preser_uva.xls"
PERIODS = [
    ("1_Trim_2025", "T125", "2025-Q1"),
    ("2_Trim_2025", "T225", "2025-Q2"),
    ("3_Trim_2025", "T325", "2025-Q3"),
    ("4_Trim_2025", "T425", "2025-Q4"),
    ("1_Trim_2026", "T126", "2026-Q1"),
]


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "NodoSantaFe/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def number(value: str) -> float:
    return float(value.replace(",", "."))


def weighted_median(values: list[tuple[float, float]]) -> float:
    values.sort(key=lambda item: item[0])
    midpoint = sum(weight for _, weight in values) / 2
    accumulated = 0.0
    for value, weight in values:
        accumulated += weight
        if accumulated >= midpoint:
            return value
    raise ValueError("No weighted observations")


def eph_household_stats(period_slug: str, file_token: str) -> dict[str, int]:
    archive = zipfile.ZipFile(io.BytesIO(download(EPH_URL.format(period=period_slug))))
    member = next(name for name in archive.namelist() if f"hogar_{file_token}" in name)
    with archive.open(member) as raw:
        rows = csv.DictReader(io.TextIOWrapper(raw, encoding="latin-1"), delimiter=";")
        households = [row for row in rows if row["AGLOMERADO"] == "10" and row["REALIZADA"] == "1"]

    income = [
        (number(row["ITF"]), number(row["PONDIH"]))
        for row in households
        if row["ITF"] not in {"", "-9"} and number(row["ITF"]) > 0
    ]
    per_capita = [
        (number(row["IPCF"]), number(row["PONDIH"]))
        for row in households
        if row["IPCF"] not in {"", "-9"} and number(row["IPCF"]) > 0
    ]
    mean_income = sum(value * weight for value, weight in income) / sum(weight for _, weight in income)
    return {
        "median": round(weighted_median(income)),
        "mean": round(mean_income),
        "median_per_capita": round(weighted_median(per_capita)),
        "sample": len(households),
        "weighted": round(sum(number(row["PONDIH"]) for row in households)),
    }


def bcra_credit() -> dict[str, float | int | str]:
    workbook = xlrd.open_workbook(file_contents=download(BCRA_UVA_URL))
    sheet = workbook.sheet_by_name("Datos")
    data_rows = [row for row in range(12, sheet.nrows) if isinstance(sheet.cell_value(row, 2), float)]
    row = data_rows[-1]
    year_month = str(int(sheet.cell_value(row, 2)))
    return {
        "period": f"{year_month[:4]}-{year_month[4:]}",
        "amount_ars": round(sheet.cell_value(row, 3) * 1000),
        "rate_pct": round(sheet.cell_value(row, 4), 2),
        "term_days": round(sheet.cell_value(row, 5)),
        "term_years": round(sheet.cell_value(row, 5) / 365.25, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/affordability-santa-fe.json")
    parser.add_argument("--fx", type=float, required=True, help="BCRA B9791 seller ARS/USD")
    parser.add_argument("--fx-date", required=True)
    parser.add_argument("--uva", type=float, required=True)
    parser.add_argument("--uva-date", required=True)
    args = parser.parse_args()

    history = []
    latest = None
    for slug, token, label in PERIODS:
        stats = eph_household_stats(slug, token)
        history.append({"period": label, "median_household_income_ars_month": stats["median"]})
        latest = stats
    assert latest is not None
    credit = bcra_credit()

    payload = {
        "schema_version": "1.0",
        "generated_at": date.today().isoformat(),
        "income": {
            "geography": "Gran Santa Fe",
            "agglomerate_code": 10,
            "latest_period": PERIODS[-1][2],
            "median_household_income_ars_month": latest["median"],
            "mean_household_income_ars_month": latest["mean"],
            "median_per_capita_income_ars_month": latest["median_per_capita"],
            "sample_households": latest["sample"],
            "weighted_households": latest["weighted"],
            "series": history,
            "source": "INDEC · Encuesta Permanente de Hogares",
            "source_url": "https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos",
            "method": "Mediana ponderada de ITF positivo con PONDIH para hogares realizados del aglomerado 10.",
            "note": "Los trimestres primero y tercero pueden incluir aguinaldo. Es una estimación propia calculada sobre microdatos oficiales, no un cuadro publicado por INDEC.",
        },
        "credit": {
            "geography": "Argentina · sistema financiero",
            "latest_period": credit["period"],
            "mortgage_uva_nominal_annual_rate_pct": credit["rate_pct"],
            "mortgage_uva_average_term_days": credit["term_days"],
            "mortgage_uva_average_term_years": credit["term_years"],
            "mortgage_uva_amount_granted_ars": credit["amount_ars"],
            "uva_ars": args.uva,
            "uva_date": args.uva_date,
            "source": "Banco Central de la República Argentina",
            "source_url": "https://www.bcra.gob.ar/tasas-de-interes/",
            "note": "La tasa es promedio ponderado de préstamos hipotecarios UVA otorgados y se adiciona a la actualización por UVA. No representa una oferta bancaria particular.",
        },
        "exchange_rate": {
            "ars_per_usd": args.fx,
            "date": args.fx_date,
            "series": "Tipo de cambio minorista ($ por USD), Comunicación B 9791, promedio vendedor",
            "source": "Banco Central de la República Argentina",
            "source_url": "https://www.bcra.gob.ar/tipo-de-cambio-minorista/",
        },
        "calculator": {
            "default_area_m2": 50,
            "default_down_payment_pct": 20,
            "purpose": "Comparar un precio publicado en USD con el ingreso mediano mensual del hogar convertido al tipo de cambio oficial de referencia.",
            "limitations": "Combina períodos distintos: ingreso EPH 2026-Q1, crédito 2026-08, tipo de cambio 2026-09-09 y mercado 2026-08/09. No estima aprobación, cuota, impuestos, gastos ni precio final de escritura.",
        },
    }
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
