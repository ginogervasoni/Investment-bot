#!/usr/bin/env python3
"""Build the compact Censo 2022 radio layer used by Nodo Santa Fe.

Counts originate in INDEC's CPV 2022 REDATAM database. The public Parquet
distribution is a reproducible conversion maintained by the ciut-redatam
project and Source Cooperative. Census geometries are distributed by CONICET.
"""

from __future__ import annotations

import json
import tempfile
from datetime import date
from pathlib import Path

import duckdb


RADIOS_URL = "https://data.source.coop/nlebovits/censo-argentino/2022/radios.parquet"
CENSUS_URL = "https://data.source.coop/nlebovits/censo-argentino/2022/census-data.parquet"
SANTA_FE_LOCAL_GOVERNMENT = "820147"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "censo-2022-santa-fe-radios.geojson"


def main() -> None:
    extension_dir = Path(tempfile.gettempdir()) / "nodo-santa-fe-duckdb-extensions"
    extension_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(config={"extension_directory": str(extension_dir)})
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute("INSTALL spatial")
    con.execute("LOAD spatial")

    query = f"""
        WITH city_radios AS (
          SELECT DISTINCT id_geo
          FROM read_parquet('{CENSUS_URL}')
          WHERE prov_code = 82
            AND valor_departamento = '063'
            AND codigo_variable = 'VIVIENDA_CODGL'
            AND valor_categoria = '{SANTA_FE_LOCAL_GOVERNMENT}'
        ),
        tenure AS (
          SELECT
            id_geo,
            SUM(conteo) AS households,
            SUM(CASE WHEN valor_categoria = '2' THEN conteo ELSE 0 END) AS rented_households
          FROM read_parquet('{CENSUS_URL}')
          WHERE codigo_variable = 'HOGAR_H22'
            AND id_geo IN (SELECT id_geo FROM city_radios)
          GROUP BY id_geo
        ),
        occupancy AS (
          SELECT
            id_geo,
            SUM(CASE WHEN valor_categoria = '1' THEN conteo ELSE 0 END) AS occupied_dwellings
          FROM read_parquet('{CENSUS_URL}')
          WHERE codigo_variable = 'VIVIENDA_V02'
            AND id_geo IN (SELECT id_geo FROM city_radios)
          GROUP BY id_geo
        )
        SELECT
          r.COD_2022 AS radio_id,
          r.POB_TOT_P AS population,
          r.VIV_TOT_P AS dwellings,
          COALESCE(t.households, 0) AS households,
          COALESCE(t.rented_households, 0) AS rented_households,
          COALESCE(o.occupied_dwellings, 0) AS occupied_dwellings,
          CASE WHEN t.households > 0
            THEN ROUND(100.0 * t.rented_households / t.households, 1)
            ELSE 0 END AS rented_pct,
          ST_AsGeoJSON(ST_SimplifyPreserveTopology(r.geometry, 0.00012)) AS geometry_json
        FROM read_parquet('{RADIOS_URL}') r
        JOIN city_radios c ON c.id_geo = r.COD_2022
        LEFT JOIN tenure t ON t.id_geo = r.COD_2022
        LEFT JOIN occupancy o ON o.id_geo = r.COD_2022
        ORDER BY r.COD_2022
    """

    features = []
    for row in con.execute(query).fetchall():
        radio_id, population, dwellings, households, rented, occupied, rented_pct, geometry = row
        features.append(
            {
                "type": "Feature",
                "id": radio_id,
                "properties": {
                    "radio": radio_id,
                    "population": int(population or 0),
                    "dwellings": int(dwellings or 0),
                    "households": int(households or 0),
                    "rented_households": int(rented or 0),
                    "occupied_dwellings": int(occupied or 0),
                    "rented_pct": float(rented_pct or 0),
                    "source": "INDEC · Censo 2022",
                },
                "geometry": json.loads(geometry),
            }
        )

    totals = {
        "radios": len(features),
        "population_private_dwellings": sum(f["properties"]["population"] for f in features),
        "dwellings": sum(f["properties"]["dwellings"] for f in features),
        "households": sum(f["properties"]["households"] for f in features),
        "rented_households": sum(f["properties"]["rented_households"] for f in features),
        "occupied_dwellings": sum(f["properties"]["occupied_dwellings"] for f in features),
    }
    totals["rented_pct"] = round(100 * totals["rented_households"] / totals["households"], 1)

    collection = {
        "type": "FeatureCollection",
        "name": "Censo 2022 · Gobierno local Santa Fe",
        "generated_at": date.today().isoformat(),
        "source": {
            "statistical": "INDEC · Censo Nacional de Población, Hogares y Viviendas 2022 · REDATAM",
            "geometry": "Cartografía de radios censales · CONICET",
            "processing": "ciut-redatam / Source Cooperative",
        },
        "scope": "Población en viviendas particulares del gobierno local Santa Fe (código 820147)",
        "totals": totals,
        "features": features,
    }
    OUTPUT.write_text(json.dumps(collection, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(totals, ensure_ascii=False, indent=2))
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
