"""Profilo opportunità spiegabile — Fase 1 (§10 dell'analisi).

NON è uno score composito: è una checklist strutturata per componenti.
Ogni componente mostra i suoi input grezzi e dichiara che le regole
NON sono validate (lo diventeranno solo con le etichette, M1-M3).
"""
from datetime import datetime, timezone

from .db import latest_observation, series

FRESH_DAYS = 7
CORE_SIGNALS = ("payout_amount", "creatives_active_count", "trend_index")

VERDE, GIALLO, ROSSO, ND = "verde", "giallo", "rosso", "n.d."


def _age_days(observed_at):
    try:
        dt = datetime.fromisoformat(str(observed_at).replace("Z", "")).replace(
            tzinfo=None
        )
    except ValueError:
        return None
    return (datetime.now(timezone.utc).replace(tzinfo=None) - dt).days


def _delta_pct(rows, window=14):
    """Variazione % tra ultimo valore e il valore ~window osservazioni prima."""
    if len(rows) < 2:
        return None
    last = rows[-1]["value"]
    base = rows[max(0, len(rows) - 1 - window)]["value"]
    if base in (None, 0):
        return None
    return (last - base) / abs(base) * 100.0


def _inp(label, value, observed_at=None):
    suffix = ""
    if observed_at:
        age = _age_days(observed_at)
        suffix = f" (osservato {age}g fa)" if age is not None else ""
    return f"{label}: {value}{suffix}"


def compute_profile(conn, opp):
    """Ritorna lista di componenti: {name, status, inputs[], explanation}."""
    oid = opp["id"]
    components = []

    # --- Domanda -----------------------------------------------------------
    trend = series(conn, oid, "trend_index")
    social = series(conn, oid, "social_mentions_7d")
    inputs, status = [], ND
    deltas = []
    if trend:
        d = _delta_pct(trend)
        deltas.append(d)
        inputs.append(_inp("trend_index", f"{trend[-1]['value']:.0f}, Δ14oss {d:+.0f}%" if d is not None else trend[-1]["value"], trend[-1]["observed_at"]))
    if social:
        d = _delta_pct(social)
        deltas.append(d)
        inputs.append(_inp("menzioni social 7g", f"{social[-1]['value']:.0f}, Δ {d:+.0f}%" if d is not None else social[-1]["value"], social[-1]["observed_at"]))
    deltas = [d for d in deltas if d is not None]
    if deltas:
        best = max(deltas)
        status = VERDE if best > 20 else (ROSSO if best < -20 else GIALLO)
    components.append({
        "name": "Domanda",
        "status": status,
        "inputs": inputs or ["nessuna osservazione"],
        "explanation": "Crescita di trend/menzioni. Soglie ±20% arbitrarie e NON validate (ipotesi A1).",
    })

    # --- Concorrenza -------------------------------------------------------
    creatives = series(conn, oid, "creatives_active_count")
    newadv = latest_observation(conn, oid, "new_advertisers_14d")
    inputs, status = [], ND
    if creatives:
        d = _delta_pct(creatives)
        inputs.append(_inp("creativi attivi", f"{creatives[-1]['value']:.0f}, Δ14oss {d:+.0f}%" if d is not None else creatives[-1]["value"], creatives[-1]["observed_at"]))
        if d is not None:
            status = ROSSO if d > 30 else (GIALLO if d > 0 else VERDE)
    if newadv:
        inputs.append(_inp("nuovi advertiser 14g", newadv["value"], newadv["observed_at"]))
    components.append({
        "name": "Concorrenza",
        "status": status,
        "inputs": inputs or ["nessuna osservazione"],
        "explanation": "Densità e momentum di ingresso (proxy dell'asta, NON l'asta: vedi B3/A13). Il segno stesso della relazione è un'ipotesi da validare.",
    })

    # --- Economics ---------------------------------------------------------
    payout = series(conn, oid, "payout_amount")
    epc = latest_observation(conn, oid, "epc_network")
    inputs, status = [], ND
    if payout:
        d = _delta_pct(payout, window=30)
        inputs.append(_inp("payout dichiarato", f"${payout[-1]['value']:.2f}, deriva {d:+.0f}%" if d is not None else f"${payout[-1]['value']:.2f}", payout[-1]["observed_at"]))
        status = VERDE if (d or 0) > 5 else (ROSSO if (d or 0) < -5 else GIALLO)
    if epc:
        inputs.append(_inp("EPC dichiarato dal network", f"${epc['value']:.2f} — DICHIARATO, non verità (§9)", epc["observed_at"]))
    components.append({
        "name": "Economics",
        "status": status,
        "inputs": inputs or ["nessuna osservazione"],
        "explanation": "Livello e deriva del payout. Payout in aumento = competizione per gli affiliati; in taglio = margini in compressione.",
    })

    # --- Durabilità --------------------------------------------------------
    age = latest_observation(conn, oid, "creative_max_age_days")
    inputs, status = [], ND
    if age and age["value"] is not None:
        v = age["value"]
        inputs.append(_inp("longevità max creativo incumbent", f"{v:.0f} giorni", age["observed_at"]))
        status = VERDE if v >= 60 else (GIALLO if v >= 30 else ROSSO)
    components.append({
        "name": "Durabilità",
        "status": status,
        "inputs": inputs or ["nessuna osservazione"],
        "explanation": "Un annuncio vivo da 60+ giorni sta quasi certamente pagando per qualcuno: rivelazione di preferenza, il segnale candidato più forte (§9.1).",
    })

    # --- Fit operativo (effort, B1/B2) -------------------------------------
    inputs = [f"approvazione: {opp['approval_status']}"]
    if opp["assets_required"] is not None:
        inputs.append(f"asset creativi richiesti: {opp['assets_required']}")
    inputs.append("prelander richiesto: " + ("sì" if opp["prelander_required"] else "no"))
    inputs.append(f"compliance: {opp['compliance_class']}")
    if opp["approval_status"] == "approvata" and opp["compliance_class"] == "white":
        status = VERDE
    elif opp["approval_status"] == "rifiutata" or opp["compliance_class"] == "black":
        status = ROSSO
    else:
        status = GIALLO
    components.append({
        "name": "Fit operativo",
        "status": status,
        "inputs": inputs,
        "explanation": "Proprietà della coppia (opportunità, operatore), non dell'opportunità: accesso (B1) + effort (B2) + compliance (B9). Un'offerta eccellente ma inaccessibile ha fit basso.",
    })

    # --- Data Confidence (meta-componente) ----------------------------------
    fresh, inputs = 0, []
    for key in CORE_SIGNALS:
        row = latest_observation(conn, oid, key)
        if row:
            a = _age_days(row["observed_at"])
            ok = a is not None and a <= FRESH_DAYS
            fresh += 1 if ok else 0
            inputs.append(f"{key}: osservato {a}g fa" + ("" if ok else " — STANTIO (B7)"))
        else:
            inputs.append(f"{key}: MAI osservato")
    ratio = fresh / len(CORE_SIGNALS)
    status = VERDE if ratio == 1 else (GIALLO if ratio >= 0.5 else ROSSO)
    components.append({
        "name": "Data confidence",
        "status": status,
        "inputs": inputs,
        "explanation": "Freschezza dei segnali core. Sotto soglia, la risposta corretta del sistema è l'astensione, non un numero tiepido (§10). Ri-verifica i termini a mano prima di ogni lancio (B7).",
    })

    return components
