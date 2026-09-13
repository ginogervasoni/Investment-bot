#!/usr/bin/env python3
"""Transfer the Mercado Libre client secret to the OAuth broker using GitHub OIDC."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


AUDIENCE = "nodo-santa-fe-meli"
BROKER = "https://nodo-santa-fe-meli.ginogervasoni.chatgpt.site/api/bootstrap"


def main() -> None:
    client_secret = os.environ.get("MELI_CLIENT_SECRET", "").strip()
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "").strip()
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "").strip()
    if not client_secret:
        raise RuntimeError("MELI_CLIENT_SECRET no está configurado")
    if not request_url or not request_token:
        raise RuntimeError("GitHub OIDC no está disponible")

    separator = "&" if "?" in request_url else "?"
    oidc_request = urllib.request.Request(
        f"{request_url}{separator}{urllib.parse.urlencode({'audience': AUDIENCE})}",
        headers={"Authorization": f"bearer {request_token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(oidc_request, timeout=30) as response:
        oidc_token = json.load(response)["value"]

    payload = json.dumps({"client_secret": client_secret}).encode("utf-8")
    sync_request = urllib.request.Request(
        BROKER,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {oidc_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(sync_request, timeout=30) as response:
        result = json.load(response)
    if result != {"ok": True}:
        raise RuntimeError("El conector rechazó la sincronización")
    print("Credencial OAuth sincronizada de forma segura")


if __name__ == "__main__":
    main()
