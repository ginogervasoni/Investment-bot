#!/usr/bin/env python3
"""Validate the aggregated Mercado Libre market dataset."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data: dict) -> None:
    assert data["schema_version"] == "1.0"
    assert data["status"] == "active"
    assert data["source"]["publisher"] == "Mercado Libre"
    assert data["source"]["api"] == "https://api.mercadolibre.com"
    assert data["source"]["site_id"] == "MLA"
    assert date.fromisoformat(data["generated_at"]) <= date.today()
    city = data["city"]
    assert city["listings"] > 0
    assert 0 <= city["sample_with_area"] <= city["listings"]
    assert city["results_collected"] <= 1000
    assert city["exact_duplicates_removed"] >= 0
    if city["sample_with_area"]:
        assert 100 <= city["median_apartment_price_usd_m2"] <= 10000
        assert city["median_sale_usd"] > 0
    for zone_id, row in data["zones"].items():
        assert zone_id in {"candioti-norte", "centro", "constituyentes", "guadalupe", "puerto", "candioti-sur", "barranquitas", "nueva-pompeya", "colastine-norte", "alto-verde"}
        assert row["listings"] > 0
        assert 0 <= row["sample_with_area"] <= row["listings"]
    forbidden = {"seller", "seller_id", "address", "latitude", "longitude", "permalink", "item_id", "listing_id", "title", "description"}

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value).union(*(keys(child) for child in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(child) for child in value)) if value else set()
        return set()

    assert not forbidden.intersection(keys(data)), "El archivo contiene campos de avisos individuales"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=ROOT / "data" / "mercadolibre-santa-fe.json")
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    current = load(args.file)
    validate(current)
    if args.previous and args.previous.exists():
        previous = load(args.previous)
        if previous.get("status") == "active":
            assert current["generated_at"] >= previous["generated_at"]
    print(f"Validación Mercado Libre correcta: {current['city']['listings']} avisos agregados")


if __name__ == "__main__":
    main()
