#!/usr/bin/env python3
"""Validate IPEC, INDEC and BCRA datasets before publication."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def month_index(period: str) -> int:
    year, month = map(int, period.split("-"))
    require(1 <= month <= 12, f"Mes inválido: {period}")
    return year * 12 + month


def quarter_index(period: str) -> int:
    year, quarter = period.split("-Q")
    require(quarter in {"1", "2", "3", "4"}, f"Trimestre inválido: {period}")
    return int(year) * 4 + int(quarter)


def validate_construction(data: dict, previous: dict | None) -> None:
    require(data.get("schema_version") == "1.0", "Esquema IPEC inválido")
    costs, permits = data["cost_gran_santa_fe"], data["permits_santa_fe_city"]
    require(len(costs) >= 12 and len(permits) >= 12, "Historia IPEC insuficiente")
    require(costs == sorted(costs, key=lambda row: row["period"]), "Costos IPEC desordenados")
    require(permits == sorted(permits, key=lambda row: row["period"]), "Permisos IPEC desordenados")
    require(data["latest_period"] == costs[-1]["period"], "El último período IPEC no coincide")
    require(all(row["total_ars_m2"] > 0 for row in costs), "Costo IPEC no positivo")
    require(all(row["authorized_m2"] >= 0 for row in permits), "Permiso IPEC negativo")
    if previous:
        require(month_index(data["latest_period"]) >= month_index(previous["latest_period"]), "El período IPEC retrocedió")


def validate_affordability(data: dict, previous: dict | None) -> None:
    require(data.get("schema_version") == "1.0", "Esquema de accesibilidad inválido")
    income, credit, exchange = data["income"], data["credit"], data["exchange_rate"]
    series = income["series"]
    require(len(series) >= 5, "Historia EPH insuficiente")
    require(series == sorted(series, key=lambda row: quarter_index(row["period"])), "Serie EPH desordenada")
    require(income["latest_period"] == series[-1]["period"], "El último período EPH no coincide")
    require(income["agglomerate_code"] == 10, "Aglomerado EPH incorrecto")
    require(income["sample_households"] >= 100, "Muestra EPH demasiado pequeña")
    require(all(row["median_household_income_ars_month"] > 0 for row in series), "Ingreso EPH no positivo")
    require(0 < credit["mortgage_uva_nominal_annual_rate_pct"] < 100, "Tasa UVA fuera de rango")
    require(365 <= credit["mortgage_uva_average_term_days"] <= 15000, "Plazo UVA fuera de rango")
    require(credit["mortgage_uva_amount_granted_ars"] > 0, "Monto UVA no positivo")
    require(credit["uva_ars"] > 0 and exchange["ars_per_usd"] > 0, "Referencia BCRA no positiva")
    date.fromisoformat(credit["uva_date"]); date.fromisoformat(exchange["date"])
    if previous:
        require(quarter_index(income["latest_period"]) >= quarter_index(previous["income"]["latest_period"]), "El período EPH retrocedió")
        require(month_index(credit["latest_period"]) >= month_index(previous["credit"]["latest_period"]), "El período de crédito retrocedió")
        require(credit["uva_date"] >= previous["credit"]["uva_date"], "La fecha UVA retrocedió")
        require(exchange["date"] >= previous["exchange_rate"]["date"], "La fecha cambiaria retrocedió")


def load(path: Path | None) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous-construction", type=Path)
    parser.add_argument("--previous-affordability", type=Path)
    parser.add_argument("--only", choices=("construction", "affordability", "all"), default="all")
    args = parser.parse_args()
    construction = load(ROOT / "data" / "construction-series.json")
    affordability = load(ROOT / "data" / "affordability-santa-fe.json")
    if args.only in {"construction", "all"}:
        validate_construction(construction, load(args.previous_construction))
    if args.only in {"affordability", "all"}:
        validate_affordability(affordability, load(args.previous_affordability))
    print(f"Validación oficial correcta: IPEC {construction['latest_period']}, EPH {affordability['income']['latest_period']}, BCRA {affordability['credit']['latest_period']}")


if __name__ == "__main__":
    main()
