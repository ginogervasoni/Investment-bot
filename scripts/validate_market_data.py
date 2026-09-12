#!/usr/bin/env python3
"""Valida el resumen inmobiliario antes de que la automatización lo publique."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "market-santa-fe.json"
EXPECTED_ZONES = {"candioti-norte", "centro", "candioti-sur", "barranquitas"}
EXPECTED_UNMATCHED = {"constituyentes", "guadalupe", "puerto", "nueva-pompeya", "colastine-norte", "alto-verde"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def iso_date(value: str) -> date:
    return date.fromisoformat(value)


def validate(data: dict, previous: dict | None = None) -> None:
    require(data.get("schema_version") == "1.0", "Versión de esquema inesperada")
    require(data.get("attribution") == "Fuente: TuLugar (tulugar.com)", "Atribución inválida")
    iso_date(data["generated_at"])

    city = data["city"]
    iso_date(city["snapshot_date"])
    require(city["listings_total"] == city["listings_sale"] + city["listings_rent"], "Los avisos de ciudad no cierran")
    for key in ("listings_total", "listings_sale", "listings_rent"):
        require(isinstance(city[key], int) and city[key] >= 0, f"Valor de ciudad inválido: {key}")
    for key in ("median_sale_usd", "median_apartment_price_usd_m2", "median_rent_usd_month"):
        require(isinstance(city[key], (int, float)) and city[key] > 0, f"Precio de ciudad inválido: {key}")

    zones = data["zones"]
    unmatched = set(data["unmatched_zone_ids"])
    require(set(zones) == EXPECTED_ZONES, "Cambió el conjunto de zonas autorizadas")
    require(unmatched == EXPECTED_UNMATCHED, "Cambió el conjunto de zonas sin asignación")
    require(set(zones).isdisjoint(unmatched), "Una zona aparece como asignada y no asignada")

    for zone_id, row in zones.items():
        require(len(row["period"]) == 7 and row["period"][4] == "-", f"Período inválido en {zone_id}")
        require(row["listings_total"] == row["listings_sale"] + row["listings_rent"], f"Los avisos no cierran en {zone_id}")
        require(row["listings_total"] > 0, f"Muestra vacía en {zone_id}")
        require(row["median_sale_usd"] > 0 and row["apartment_price_usd_m2"] > 0, f"Precio inválido en {zone_id}")
        require(row["match"] in {"exact", "spelling_variant"}, f"Tipo de coincidencia inválido en {zone_id}")
        parsed = urlparse(row["source_page"])
        require(parsed.scheme == "https" and parsed.netloc == "tulugar.com", f"Fuente inválida en {zone_id}")

    for url in data["sources"].values():
        parsed = urlparse(url)
        require(parsed.scheme == "https" and parsed.netloc == "tulugar.com", "Enlace de fuente inválido")

    if previous:
        require(city["snapshot_date"] >= previous["city"]["snapshot_date"], "La fotografía de ciudad retrocedió")
        for zone_id in EXPECTED_ZONES:
            require(zones[zone_id]["period"] >= previous["zones"][zone_id]["period"], f"El período retrocedió en {zone_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", nargs="?", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
    validate(data, previous)
    print(f"Validación correcta: {len(data['zones'])} zonas, snapshot {data['city']['snapshot_date']}")


if __name__ == "__main__":
    main()
