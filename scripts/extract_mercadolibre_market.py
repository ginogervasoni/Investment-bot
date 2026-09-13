#!/usr/bin/env python3
"""Aggregate Santa Fe apartment listings through Mercado Libre's official API.

The exported JSON contains statistics only. Individual listing IDs, sellers,
addresses and coordinates are deliberately not persisted.
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "mercadolibre-santa-fe.json"
AFFORDABILITY = ROOT / "data" / "affordability-santa-fe.json"
API = "https://api.mercadolibre.com"
SITE_ID = "MLA"
REAL_ESTATE_CATEGORY = "MLA1459"
PAGE_SIZE = 50
MAX_RESULTS = 1000

ZONE_ALIASES = {
    "candioti-norte": {"candioti norte", "barrio candioti norte"},
    "centro": {"centro", "microcentro", "barrio centro"},
    "constituyentes": {"constituyentes", "barrio constituyentes"},
    "guadalupe": {"guadalupe", "guadalupe oeste", "guadalupe este"},
    "puerto": {"puerto", "puerto santa fe", "dique ii", "dique 2"},
    "candioti-sur": {"candioti sur", "candioti sud", "barrio candioti sur"},
    "barranquitas": {"barranquitas", "barrio barranquitas"},
    "nueva-pompeya": {"nueva pompeya", "pompeya"},
    "colastine-norte": {"colastine norte"},
    "alto-verde": {"alto verde"},
}


def normalized(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).lower().split())


def application_token() -> str:
    """Return an API token without persisting credentials or tokens.

    A pre-existing user token remains supported for backwards compatibility.
    The normal automated path exchanges the application's Client ID and Secret
    through Mercado Libre's official client-credentials grant on every run.
    """
    configured = os.environ.get("MELI_ACCESS_TOKEN", "").strip()
    if configured:
        return configured

    client_id = os.environ.get("MELI_CLIENT_ID", "").strip()
    client_secret = os.environ.get("MELI_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("Faltan MELI_CLIENT_ID y MELI_CLIENT_SECRET")

    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{API}/oauth/token",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "NodoSantaFe/1.0 (market research; aggregated output)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        response_body = error.read(500).decode("utf-8", errors="replace")
        raise RuntimeError(f"Mercado Libre OAuth HTTP {error.code}: {response_body}") from error
    token = str(payload.get("access_token") or "").strip() if isinstance(payload, dict) else ""
    if not token:
        raise RuntimeError("Mercado Libre no devolvió un access_token de aplicación")
    return token


def api_get(path: str, token: str, params: dict[str, object] | None = None) -> object:
    query = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{API}{path}{'?' + query if query else ''}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "NodoSantaFe/1.0 (market research; aggregated output)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read(500).decode("utf-8", errors="replace")
        raise RuntimeError(f"Mercado Libre API HTTP {error.code}: {body}") from error


def attribute(item: dict, *ids: str) -> object | None:
    wanted = set(ids)
    for row in item.get("attributes") or []:
        if row.get("id") in wanted:
            return row.get("value_name") if row.get("value_name") is not None else row.get("value_id")
    return None


def number(value: object) -> float | None:
    if value is None:
        return None
    candidate = str(value).lower().replace("m²", "").replace("m2", "").replace(",", ".").strip()
    try:
        result = float(candidate.split()[0])
        return result if result > 0 else None
    except (ValueError, IndexError):
        return None


def city_id(token: str) -> str:
    rows = api_get("/classified_locations/countries/AR/search", token, {"city": "Santa Fe"})
    if not isinstance(rows, list):
        raise RuntimeError("La API no devolvió una lista de localidades")
    for row in rows:
        if normalized(row.get("city", {}).get("name")) == "santa fe" and normalized(row.get("state", {}).get("name")) == "santa fe":
            return row["city"]["id"]
    raise RuntimeError("No se encontró Santa Fe Capital en classified_locations")


def item_details(ids: list[str], token: str) -> list[dict]:
    if not ids:
        return []
    response = api_get("/items", token, {"ids": ",".join(ids)})
    if not isinstance(response, list):
        raise RuntimeError("La API no devolvió el detalle esperado")
    return [row["body"] for row in response if row.get("code") == 200 and isinstance(row.get("body"), dict)]


def is_apartment_sale(item: dict) -> bool:
    property_type = normalized(attribute(item, "PROPERTY_TYPE", "REAL_ESTATE_TYPE"))
    operation = normalized(attribute(item, "OPERATION", "OPERATION_TYPE"))
    title = normalized(item.get("title"))
    apartment = "departamento" in property_type or "departamento" in title or "depto" in title
    sale = "venta" in operation or ("alquiler" not in operation and "alquiler" not in title)
    return apartment and sale


def neighborhood(item: dict) -> str:
    location = item.get("location") or {}
    return str((location.get("neighborhood") or {}).get("name") or "").strip()


def zone_for(name: str) -> str | None:
    value = normalized(name)
    for zone_id, aliases in ZONE_ALIASES.items():
        if value in aliases:
            return zone_id
    return None


def usd_values(item: dict, ars_per_usd: float) -> tuple[float, float] | None:
    price = number(item.get("price"))
    area = number(attribute(item, "TOTAL_AREA", "COVERED_AREA"))
    if not price or not area or area < 15 or area > 600:
        return None
    currency = item.get("currency_id")
    if currency == "ARS":
        price /= ars_per_usd
    elif currency != "USD":
        return None
    price_m2 = price / area
    if not 100 <= price_m2 <= 10000:
        return None
    return price, price_m2


def median(rows: list[float]) -> float | None:
    return round(statistics.median(rows), 2) if rows else None


def aggregate(rows: list[dict], ars_per_usd: float) -> dict:
    prices: list[float] = []
    prices_m2: list[float] = []
    neighborhoods: dict[str, int] = {}
    for item in rows:
        name = neighborhood(item)
        if name:
            neighborhoods[name] = neighborhoods.get(name, 0) + 1
        values = usd_values(item, ars_per_usd)
        if values:
            price, price_m2 = values
            prices.append(price)
            prices_m2.append(price_m2)
    return {
        "listings": len(rows),
        "sample_with_area": len(prices_m2),
        "median_sale_usd": median(prices),
        "median_apartment_price_usd_m2": median(prices_m2),
        "neighborhoods": sorted(neighborhoods, key=neighborhoods.get, reverse=True)[:5],
    }


def main() -> None:
    token = application_token()

    ars_per_usd = json.loads(AFFORDABILITY.read_text(encoding="utf-8"))["exchange_rate"]["ars_per_usd"]
    santa_fe_city_id = city_id(token)
    raw: list[dict] = []
    total_available = 0
    offset = 0
    while offset < MAX_RESULTS:
        page = api_get(
            f"/sites/{SITE_ID}/search",
            token,
            {
                "category": REAL_ESTATE_CATEGORY,
                "city": santa_fe_city_id,
                "q": "departamento venta",
                "limit": PAGE_SIZE,
                "offset": offset,
            },
        )
        if not isinstance(page, dict):
            raise RuntimeError("Respuesta de búsqueda inválida")
        total_available = int((page.get("paging") or {}).get("total") or 0)
        summaries = page.get("results") or []
        if not summaries:
            break
        raw.extend(item_details([row["id"] for row in summaries if row.get("id")], token))
        offset += len(summaries)
        if offset >= min(total_available, MAX_RESULTS):
            break

    unique = {item["id"]: item for item in raw if item.get("id")}
    eligible = [item for item in unique.values() if is_apartment_sale(item) and normalized(((item.get("location") or {}).get("city") or {}).get("name")) == "santa fe"]
    by_zone: dict[str, list[dict]] = {}
    unmatched = 0
    for item in eligible:
        zone_id = zone_for(neighborhood(item))
        if zone_id:
            by_zone.setdefault(zone_id, []).append(item)
        else:
            unmatched += 1

    city = aggregate(eligible, ars_per_usd)
    city.update(
        {
            "total_available_from_api": total_available,
            "results_collected": len(raw),
            "exact_duplicates_removed": len(raw) - len(unique),
            "unmatched_neighborhood_listings": unmatched,
            "snapshot_date": date.today().isoformat(),
        }
    )
    zones = {}
    for zone_id, items in sorted(by_zone.items()):
        row = aggregate(items, ars_per_usd)
        row["match"] = "verified_alias"
        zones[zone_id] = row

    payload = {
        "schema_version": "1.0",
        "status": "active",
        "generated_at": date.today().isoformat(),
        "source": {
            "publisher": "Mercado Libre",
            "product": "Mercado Libre Inmuebles",
            "classification": "authorized-market-api-derived",
            "api": "https://api.mercadolibre.com",
            "documentation": "https://developers.mercadolibre.com.ar/",
            "site_id": SITE_ID,
            "city_id": santa_fe_city_id,
            "category_id": REAL_ESTATE_CATEGORY,
        },
        "scope": "Departamentos publicados en venta en Santa Fe Capital",
        "city": city,
        "zones": zones,
        "privacy": "Solo se publican agregados. No se almacenan IDs, vendedores, direcciones, coordenadas ni descripciones de avisos.",
        "limitations": "Son precios de oferta, no de cierre. La búsqueda puede estar limitada por la API y una baja de publicación no prueba una venta.",
        "payload_fingerprint": hashlib.sha256(json.dumps({"city": city, "zones": zones}, sort_keys=True).encode()).hexdigest(),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mercado Libre: {city['listings']} departamentos; {city['sample_with_area']} con superficie; {len(zones)} zonas")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error del conector Mercado Libre: {error}", file=sys.stderr)
        raise SystemExit(1) from error
