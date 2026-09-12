#!/usr/bin/env python3
"""Descarga y resume datos abiertos de oferta inmobiliaria de TuLugar.

La salida contiene únicamente indicadores agregados necesarios para Nodo. La
fuente permite reutilización comercial con atribución y no permite re-alojar
los conjuntos completos como un catálogo propio.
"""

from __future__ import annotations

import csv
import io
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "market-santa-fe.json"
BASE = "https://tulugar.com/api/market-data"
CITY_SLUG = "santa-fe"

ZONE_MATCHES = {
    "candioti-norte": {"slug": "candioti-norte", "label": "Candioti Norte", "match": "exact"},
    "centro": {"slug": "centro", "label": "Centro", "match": "exact"},
    "candioti-sur": {"slug": "candioti-sud", "label": "Candioti Sud", "match": "spelling_variant"},
    "barranquitas": {"slug": "barranquitas", "label": "Barranquitas", "match": "exact"},
}


def update_catalog(payload: dict) -> None:
    path = ROOT / "data" / "source-catalog.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    source = next(item for item in catalog["sources"] if item["id"] == "tulugar_santa_fe_market")
    source["latest_snapshot"] = payload["city"]["snapshot_date"]
    source["latest_monthly_period"] = max(zone["period"] for zone in payload["zones"].values())
    source["accessed_at"] = payload["generated_at"]
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download_rows(**params: str) -> list[dict[str, str]]:
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "Nodo-Santa-Fe/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(content)))


def number(value: str, *, integer: bool = False):
    if value in (None, ""):
        return None
    parsed = float(value)
    return int(parsed) if integer else round(parsed, 2)


def main() -> None:
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    snapshot = download_rows(country="argentina", dataset="snapshot")
    city = next(row for row in snapshot if row["city_slug"] == CITY_SLUG)

    zones = {}
    for zone_id, match in ZONE_MATCHES.items():
        rows = download_rows(
            country="argentina",
            city=CITY_SLUG,
            neighborhood=match["slug"],
            dataset="sale",
        )
        latest = rows[-1]
        zones[zone_id] = {
            "source_neighborhood": match["label"],
            "source_slug": match["slug"],
            "match": match["match"],
            "period": latest["month"][:7],
            "listings_total": number(latest["active_listings_eom"], integer=True),
            "listings_sale": number(latest["active_listings_sale_eom"], integer=True),
            "listings_rent": number(latest["active_listings_rent_eom"], integer=True),
            "median_sale_usd": number(latest["median_sale_price_usd"]),
            "apartment_price_usd_m2": number(latest["median_apartment_ppsqm_usd"]),
            "median_rent_usd_month": number(latest["median_rent_price_usd"]),
            "source_page": f"https://tulugar.com/es/mercado/argentina/santa-fe/{match['slug']}",
        }

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "classification": "authorized-market-data-derived",
        "attribution": "Fuente: TuLugar (tulugar.com)",
        "city": {
            "name": city["city_name"],
            "snapshot_date": city["stats_date"],
            "listings_total": number(city["active_listings_total"], integer=True),
            "listings_sale": number(city["active_listings_sale"], integer=True),
            "listings_rent": number(city["active_listings_rent"], integer=True),
            "median_sale_usd": number(city["median_sale_price_usd"]),
            "median_apartment_price_usd_m2": number(city["median_sale_price_per_sqm_usd"]),
            "median_rent_usd_month": number(city["median_rent_price_usd"]),
        },
        "zones": zones,
        "unmatched_zone_ids": [
            "constituyentes", "guadalupe", "puerto", "nueva-pompeya",
            "colastine-norte", "alto-verde",
        ],
        "methodology": {
            "price_type": "asking_prices",
            "sale_m2_definition": "Mediana USD/m² de departamentos en venta",
            "rent_definition": "Mediana mensual de avisos de alquiler, en USD",
            "minimum_scope_rule": "Only exact neighborhood matches or documented spelling variants are assigned to app zones",
            "limitations": "Son precios publicados, no precios finales de escritura. La serie mensual argentina comienza en 2026 y todavía no permite estimar valorización anual.",
        },
        "sources": {
            "open_data": "https://tulugar.com/es/datos",
            "methodology": "https://tulugar.com/es/mercado/paraguay/metodologia",
            "city_market": "https://tulugar.com/es/mercado/argentina/santa-fe",
        },
    }
    if previous:
        comparable = {key: value for key, value in payload.items() if key != "generated_at"}
        previous_comparable = {key: value for key, value in previous.items() if key != "generated_at"}
        if comparable == previous_comparable:
            payload["generated_at"] = previous["generated_at"]
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    changed = not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered
    OUT.write_text(rendered, encoding="utf-8")
    update_catalog(payload)
    print(f"{'Actualizado' if changed else 'Sin cambios'} {OUT} ({len(zones)} zonas con coincidencia válida)")


if __name__ == "__main__":
    main()
