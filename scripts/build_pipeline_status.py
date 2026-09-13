#!/usr/bin/env python3
"""Create the public status summary after all data validations pass."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def connector_status(name: str) -> str:
    return "active" if os.environ.get(f"PIPELINE_{name.upper()}_STATUS", "success") == "success" else "error"


def detail(status: str, healthy_text: str) -> str:
    return healthy_text if status == "active" else "fuente no disponible; se conserva el último dato válido"


def main() -> None:
    market = read("market-santa-fe.json")
    construction = read("construction-series.json")
    affordability = read("affordability-santa-fe.json")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    statuses = {name: connector_status(name) for name in ("market", "ipec", "indec_bcra")}
    payload = {
        "schema_version": "1.0",
        "checked_at": now.isoformat().replace("+00:00", "Z"),
        "schedule": {"frequency": "monthly", "day": 1, "time": "08:17", "timezone": "America/Argentina/Cordoba"},
        "status": "healthy" if all(value == "active" for value in statuses.values()) else "degraded",
        "connectors": {
            "tulugar": {"label": "Mercado", "publisher": "TuLugar", "status": statuses["market"], "latest_period": market["city"]["snapshot_date"], "cadence": "mensual", "detail": detail(statuses["market"], f"{len(market['zones'])} zonas verificadas")},
            "ipec": {"label": "Construcción", "publisher": "IPEC", "status": statuses["ipec"], "latest_period": construction["latest_period"], "cadence": "mensual", "detail": detail(statuses["ipec"], "costos y permisos")},
            "indec": {"label": "Ingresos", "publisher": "INDEC · EPH", "status": statuses["indec_bcra"], "latest_period": affordability["income"]["latest_period"], "cadence": "trimestral", "detail": detail(statuses["indec_bcra"], "Gran Santa Fe")},
            "bcra": {"label": "Crédito y dólar", "publisher": "BCRA", "status": statuses["indec_bcra"], "latest_period": affordability["exchange_rate"]["date"], "cadence": "diaria/mensual", "detail": detail(statuses["indec_bcra"], f"hipotecarios {affordability['credit']['latest_period']}")},
        },
        "publication_rule": "El estado se publica únicamente después de que todos los validadores finalizan correctamente.",
    }
    (DATA / "pipeline-status.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Estado {payload['status']} generado: {payload['checked_at']}")


if __name__ == "__main__":
    main()
