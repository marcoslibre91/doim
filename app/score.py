"""Profilo opportunità spiegabile — Fase 1 (§10 dell'analisi).

NON è uno score composito: è una checklist strutturata per componenti.
Ogni componente mostra i suoi input grezzi, una lettura in chiaro (headline),
la direzione del trend e dichiara che le regole NON sono validate (M1-M3).
"""
from datetime import datetime, timezone

from .db import latest_observation, series

FRESH_DAYS = 7
CORE_SIGNALS = ("payout_amount", "creatives_active_count", "trend_index")

VERDE, GIALLO, ROSSO, ND = "verde", "giallo", "rosso", "n.d."
SU, GIU, STABILE = "↑", "↓", "→"


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


def _arrow(delta):
    if delta is None:
        return ""
    if delta > 5:
        return SU
    if delta < -5:
        return GIU
    return STABILE


def _inp(label, value, observed_at=None):
    suffix = ""
    if observed_at:
        age = _age_days(observed_at)
        suffix = f" (osservato {age}g fa)" if age is not None else ""
    return f"{label}: {value}{suffix}"


def _comp(name, status, headline, arrow, inputs, explanation, threshold):
    return {
        "name": name,
        "status": status,
        "headline": headline,
        "arrow": arrow,
        "inputs": inputs or ["nessuna osservazione"],
        "explanation": explanation,
        "threshold": threshold,
    }


def compute_profile(conn, opp):
    """Ritorna lista di componenti leggibili per la UI."""
    oid = opp["id"]
    components = []

    # --- Domanda -----------------------------------------------------------
    trend = series(conn, oid, "trend_index")
    social = series(conn, oid, "social_mentions_7d")
    inputs, status, deltas = [], ND, []
    if trend:
        d = _delta_pct(trend)
        deltas.append(d)
        inputs.append(_inp("trend_index", f"{trend[-1]['value']:.0f}, Δ {d:+.0f}%" if d is not None else trend[-1]["value"], trend[-1]["observed_at"]))
    if social:
        d = _delta_pct(social)
        deltas.append(d)
        inputs.append(_inp("menzioni social 7g", f"{social[-1]['value']:.0f}, Δ {d:+.0f}%" if d is not None else social[-1]["value"], social[-1]["observed_at"]))
    deltas = [d for d in deltas if d is not None]
    best = max(deltas) if deltas else None
    if best is not None:
        status = VERDE if best > 20 else (ROSSO if best < -20 else GIALLO)
    headline = {VERDE: "Interesse in crescita", GIALLO: "Interesse stabile",
                ROSSO: "Interesse in calo", ND: "Domanda non osservata"}[status]
    components.append(_comp(
        "Domanda", status, headline, _arrow(best), inputs,
        "Quanto cresce l'interesse del pubblico (ricerca + menzioni social). Se sale mentre la concorrenza resta ferma, è la definizione di opportunità.",
        "Soglia ±20% — arbitraria e NON validata (ipotesi A1)."))

    # --- Concorrenza -------------------------------------------------------
    creatives = series(conn, oid, "creatives_active_count")
    newadv = latest_observation(conn, oid, "new_advertisers_14d")
    inputs, status, d = [], ND, None
    if creatives:
        d = _delta_pct(creatives)
        inputs.append(_inp("creativi attivi", f"{creatives[-1]['value']:.0f}, Δ {d:+.0f}%" if d is not None else creatives[-1]["value"], creatives[-1]["observed_at"]))
        if d is not None:
            status = ROSSO if d > 30 else (GIALLO if d > 0 else VERDE)
    if newadv:
        inputs.append(_inp("nuovi advertiser 14g", newadv["value"], newadv["observed_at"]))
    headline = {VERDE: "Concorrenza in calo (spazio libero)", GIALLO: "Concorrenza in aumento",
                ROSSO: "Affollamento rapido (rischio saturazione)", ND: "Concorrenza non osservata"}[status]
    components.append(_comp(
        "Concorrenza", status, headline, _arrow(d), inputs,
        "Quanti stanno già promuovendo l'offerta e con che velocità entrano. Attenzione: è un proxy dell'asta pubblicitaria, NON l'asta vera (B3/A13).",
        "Crescita creativi >30% = rosso; il segno stesso della relazione con l'esito è un'ipotesi."))

    # --- Economics ---------------------------------------------------------
    payout = series(conn, oid, "payout_amount")
    epc = latest_observation(conn, oid, "epc_network")
    inputs, status, d = [], ND, None
    if payout:
        d = _delta_pct(payout, window=30)
        inputs.append(_inp("payout dichiarato", f"${payout[-1]['value']:.2f}, deriva {d:+.0f}%" if d is not None else f"${payout[-1]['value']:.2f}", payout[-1]["observed_at"]))
        status = VERDE if (d or 0) > 5 else (ROSSO if (d or 0) < -5 else GIALLO)
    if epc:
        inputs.append(_inp("EPC dichiarato dal network", f"${epc['value']:.2f} — DICHIARATO, non verità", epc["observed_at"]))
    headline = {VERDE: "Payout in aumento (domanda di traffico)", GIALLO: "Payout stabile",
                ROSSO: "Payout in taglio (margini in compressione)", ND: "Economics non osservati"}[status]
    components.append(_comp(
        "Economics", status, headline, _arrow(d), inputs,
        "Quanto paga l'offerta e come cambia nel tempo. Payout in aumento = il network compete per gli affiliati; in taglio = margini che si stringono.",
        "Deriva payout ±5% su 30 osservazioni. L'EPC del network è marketing, non verità."))

    # --- Durabilità --------------------------------------------------------
    age = latest_observation(conn, oid, "creative_max_age_days")
    inputs, status, v = [], ND, None
    if age and age["value"] is not None:
        v = age["value"]
        inputs.append(_inp("longevità max creativo incumbent", f"{v:.0f} giorni", age["observed_at"]))
        status = VERDE if v >= 60 else (GIALLO if v >= 30 else ROSSO)
    headline = {VERDE: "Offerta collaudata (qualcuno ci guadagna da mesi)", GIALLO: "Durabilità media",
                ROSSO: "Offerta giovane o volatile", ND: "Durabilità non osservata"}[status]
    components.append(_comp(
        "Durabilità", status, headline, "", inputs,
        "Da quanto è vivo il creativo più longevo. Un annuncio attivo da 60+ giorni sta quasi certamente pagando per qualcuno: è il segnale candidato più forte (rivelazione di preferenza).",
        "≥60g verde, 30-60g giallo, <30g rosso."))

    # --- Fit operativo (effort, B1/B2/B9) ----------------------------------
    inputs = [f"approvazione: {opp['approval_status']}"]
    if opp["assets_required"] is not None:
        inputs.append(f"asset creativi richiesti: {opp['assets_required']}")
    inputs.append("prelander richiesto: " + ("sì" if opp["prelander_required"] else "no"))
    inputs.append(f"compliance: {opp['compliance_class']}")
    if opp["approval_status"] == "approvata" and opp["compliance_class"] == "white":
        status, headline = VERDE, "Pronta da lanciare"
    elif opp["approval_status"] == "rifiutata" or opp["compliance_class"] == "black":
        status, headline = ROSSO, "Inaccessibile o troppo rischiosa"
    else:
        status, headline = GIALLO, "Serve lavoro prima di lanciare"
    components.append(_comp(
        "Fit operativo", status, headline, "", inputs,
        "Quanto è accessibile e fattibile PER TE: approvazione (B1), effort di lancio (B2), rischio compliance (B9). Un'offerta eccellente ma inaccessibile in tempo utile vale poco.",
        "Verde solo se approvata + white. È una proprietà della coppia (offerta, operatore), non dell'offerta."))

    # --- Data Confidence (meta-componente) ----------------------------------
    fresh, inputs = 0, []
    for key in CORE_SIGNALS:
        row = latest_observation(conn, oid, key)
        if row:
            a = _age_days(row["observed_at"])
            ok = a is not None and a <= FRESH_DAYS
            fresh += 1 if ok else 0
            inputs.append(f"{key}: osservato {a}g fa" + ("" if ok else " — STANTIO"))
        else:
            inputs.append(f"{key}: MAI osservato")
    ratio = fresh / len(CORE_SIGNALS)
    status = VERDE if ratio == 1 else (GIALLO if ratio >= 0.5 else ROSSO)
    headline = {VERDE: "Dati freschi, ci si può fidare", GIALLO: "Alcuni dati sono vecchi",
                ROSSO: "Dati troppo vecchi per decidere"}[status]
    components.append(_comp(
        "Data confidence", status, headline, "", inputs,
        "Quanto sono freschi i segnali principali. Sotto soglia, la risposta corretta del sistema è l'astensione, non un giudizio tiepido. Ri-verifica i termini a mano prima di ogni lancio (B7).",
        f"Verde solo se tutti i {len(CORE_SIGNALS)} segnali core osservati negli ultimi {FRESH_DAYS} giorni."))

    return components


def profile_summary(components):
    """Riepilogo a colpo d'occhio: conteggio semafori + eventuale allarme dati."""
    counts = {VERDE: 0, GIALLO: 0, ROSSO: 0, ND: 0}
    data_conf = ND
    for c in components:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
        if c["name"] == "Data confidence":
            data_conf = c["status"]
    return {"counts": counts, "data_conf": data_conf}
