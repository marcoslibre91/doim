"""Connettore Everflow — per network affiliate che girano su piattaforma Everflow
(GiddyUp e diversi altri network "pro").

USO LEGITTIMO SOLTANTO: questo connettore accede ai dati del TUO account
affiliato tramite l'API ufficiale, con la API key personale generata dal
pannello (Account → API Keys). Non fa scraping e non tocca dati altrui —
coerente con la strategia "fonti con diritto d'accesso stabile" (A4).

Uso:
    export EVERFLOW_API_KEY=...
    python -m app.connectors            # scarica le offerte visibili e registra payout come osservazioni

Cosa registra:
    payout_amount  — payout dichiarato per ogni offerta visibile al tuo account

Estensioni ovvie (stesso pattern): /v1/affiliates/reporting per click,
conversioni e EPC reale del proprio traffico (segnale epc_real).
"""
import json
import os
import urllib.request
from datetime import date

from .db import get_conn, init_db

BASE = os.environ.get("EVERFLOW_BASE", "https://api.eflow.team")


def _get(path):
    key = os.environ.get("EVERFLOW_API_KEY")
    if not key:
        raise SystemExit("EVERFLOW_API_KEY mancante: generala dal pannello affiliato del network.")
    req = urllib.request.Request(
        BASE + path,
        headers={"X-Eflow-API-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def pull_offers(network_label="GiddyUp"):
    """Scarica le offerte visibili al proprio account e registra il payout di oggi."""
    init_db()
    conn = get_conn()
    src = conn.execute(
        "SELECT id FROM sources WHERE name LIKE ? LIMIT 1", (f"%{network_label}%",)
    ).fetchone()
    src_id = src["id"] if src else None
    sig = conn.execute(
        "SELECT id FROM signals WHERE key='payout_amount' ORDER BY version DESC LIMIT 1"
    ).fetchone()["id"]

    data = _get("/v1/affiliates/offersrunable")
    offers = data.get("offers", data if isinstance(data, list) else [])
    imported = 0
    for off in offers:
        okey = f"{network_label.lower()}-{off.get('network_offer_id', off.get('id'))}"
        row = conn.execute("SELECT id FROM opportunities WHERE key=?", (okey,)).fetchone()
        if row:
            oid = row["id"]
        else:
            cur = conn.execute(
                "INSERT INTO opportunities(key,name,network,state) VALUES (?,?,?, 'rilevata')",
                (okey, off.get("name", okey), network_label))
            oid = cur.lastrowid
        payout = None
        try:
            payout = float(off.get("payout", {}).get("payout_amount", off.get("default_payout")))
        except (TypeError, ValueError):
            pass
        if payout is not None:
            conn.execute(
                "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
                "VALUES (?,?,?,?,?)", (oid, sig, payout, date.today().isoformat(), src_id))
            imported += 1
    conn.commit()
    conn.close()
    print(f"{len(offers)} offerte viste, {imported} osservazioni payout registrate.")


if __name__ == "__main__":
    pull_offers()
