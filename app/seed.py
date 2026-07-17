"""Seed del database: fonti, segnali versionati, registro ipotesi A1-A13.

Con --demo aggiunge 3 opportunità dimostrative (chiaramente marcate demo-*)
con 30 giorni di osservazioni sintetiche, per vedere la piattaforma popolata.
"""
import math
import sys
from datetime import date, timedelta

from .db import get_conn, init_db

SOURCES = [
    ("GiddyUp (Everflow API, account proprio)", "affiliate_network", "api_ufficiale", "basso"),
    ("Report CSV network", "affiliate_network", "export_csv", "basso"),
    ("Meta Ad Library", "ad_library", "manuale", "medio"),
    ("Google Trends", "trend", "manuale", "basso"),
    ("Sonda micro-spend (proprio)", "probe", "manuale", "basso"),
    ("Tracking proprio (postback)", "own_tracking", "api_ufficiale", "basso"),
    ("Osservazione manuale", "manuale", "manuale", "basso"),
]

SIGNALS = [
    ("payout_amount", "Payout dichiarato dal network (USD)", "A",
     "Dichiarato, non verificato: osservabile è l'annuncio, non la sua verità (§8.A)."),
    ("epc_network", "EPC dichiarato dal network (USD)", "A",
     "Marketing del network: usabile solo come variazione, mai come stima del proprio risultato (§9)."),
    ("creatives_active_count", "N. creativi attivi in ad library per l'offerta", "A",
     "Densità competitiva osservabile. Proxy dell'asta, NON l'asta (B3/A13)."),
    ("creative_max_age_days", "Longevità max di un creativo incumbent (giorni)", "A",
     "Rivelazione di preferenza: 60+ giorni ⇒ quasi certamente profittevole per qualcuno (§9.1)."),
    ("new_advertisers_14d", "Nuovi advertiser entrati negli ultimi 14 giorni", "A",
     "Momentum competitivo: il segno della relazione con l'outcome è un'ipotesi (§9.2)."),
    ("trend_index", "Indice Google Trends (0-100, relativo)", "A",
     "Indice relativo, non volume assoluto."),
    ("social_mentions_7d", "Menzioni social pubbliche negli ultimi 7 giorni", "A",
     "Volume, non sentiment (il sentiment generico è dichiarato inutile, §9)."),
    ("cpm_probe", "CPM misurato con sonda micro-spend (USD)", "A",
     "L'unico modo di osservare l'asta: pagare poco per misurare (B3). Costo = acquisizione dati."),
    ("saturation_index", "Indice di saturazione stimato (0-1)", "B",
     "STIMA da densità + velocità d'ingresso: viaggia sempre col suo errore (§8.B)."),
    ("approval_latency_days", "Latenza di approvazione misurata (giorni)", "A",
     "Dato proprio: quanto ha impiegato il network ad approvarci (B1)."),
    ("epc_real", "EPC reale dal tracking proprio (USD)", "A",
     "Verità propria — al netto della riconciliazione col network (B4)."),
]

HYPOTHESES = [
    ("A1", "Esistono segnali osservabili pubblicamente che precedono il successo economico di un'opportunità.",
     "Studio retrospettivo su storia ricostruita (settimane 2-8) + previsioni pre-registrate out-of-sample nel journal.",
     "Nessun segnale supera la retrospettiva corretta per test multipli, e il journal a 6 mesi non batte il base rate."),
    ("A2", "Il vantaggio temporale del segnale è abbastanza lungo da agire prima della saturazione.",
     "Misurare il lag segnale→saturazione su coorti storiche, inclusa la latenza di approvazione (B1).",
     "Lag mediano < latenza mediana di approvazione + tempo di lancio."),
    ("A3", "La serie storica ha valore composto (più storico ⇒ decisioni migliori).",
     "Confrontare accuratezza predittiva con finestre 3/6/12 mesi.",
     "Plateau di accuratezza già a 3 mesi."),
    ("A4", "Le fonti resteranno accessibili a costo sostenibile per anni.",
     "Audit fonte per fonte (accesso, ToS, piano B); iniziare dalle 2-3 fonti del pilota.",
     "Meno di 2 fonti core con diritto d'accesso stabile."),
    ("A5", "Le opportunità sono confrontabili tra loro (metrica comune cross-verticale sensata).",
     "Test di stabilità dei predittori tra 2+ verticali (Q3).",
     "Predittori completamente idiosincratici per verticale."),
    ("A6", "L'outcome di un'allocazione misura la qualità dell'opportunità, non solo dell'esecuzione.",
     "Allocazioni ripetute sulla stessa opportunità con esecuzioni diverse; incidenti registrati come covariate (B8).",
     "Varianza tra esecuzioni >> varianza tra opportunità."),
    ("A7", "Il numero di allocazioni interne genera etichette sufficienti per imparare.",
     "Contare le etichette/anno realistiche; anello di calibrazione a etichette gratuite come compensazione.",
     "< 100 etichette/anno e nessuna via (consorzio, etichette osservazionali) per moltiplicarle."),
    ("A8", "I segnali pubblici non sono già completamente arbitrati da chi li guarda ogni giorno.",
     "Coincide con A1 in forma prospettica: se A1 regge out-of-sample, A8 regge.",
     "Come A1."),
    ("A9", "I predittori restano stabili nonostante i regime change delle piattaforme.",
     "Test di stabilità temporale attraverso eventi noti (update algoritmi, policy).",
     "I predittori di Q2 non valgono più sui dati di Q4."),
    ("A10", "Il sistema batte (o migliora misurabilmente) l'intuizione dell'operatore esperto.",
     "Torneo nel journal: sistema vs umano vs selezione casuale, stesso capitale (Q3).",
     "Il braccio sistema non batte il braccio casuale nemmeno in direzione."),
    ("A11", "Esiste un mercato disposto a pagare, se si commercializza.",
     "RINVIATA: irrilevante finché A1 non è dimostrata.",
     "—"),
    ("A12", "I dati raccolti oggi saranno interpretabili tra 3 anni.",
     "Disciplina di versioning dei segnali (già nel modello dati): è una scelta, non un fatto.",
     "Cambi di definizione non versionati."),
    ("A13", "La densità osservabile di creativi è un proxy utilizzabile della pressione d'asta reale.",
     "Sonde micro-spend: confrontare CPM misurati con densità osservata per angle × geo (B3).",
     "Correlazione nulla o instabile tra densità e CPM sondato."),
]


def seed_base(conn):
    for name, kind, access, risk in SOURCES:
        conn.execute(
            "INSERT OR IGNORE INTO sources(name,kind,access_mode,tos_risk) VALUES (?,?,?,?)",
            (name, kind, access, risk))
    for key, name, tier, definition in SIGNALS:
        conn.execute(
            "INSERT OR IGNORE INTO signals(key,version,name,tier,definition) VALUES (?,1,?,?,?)",
            (key, name, tier, definition))
    for code, statement, test, kill in HYPOTHESES:
        conn.execute(
            "INSERT OR IGNORE INTO hypotheses(code,statement,test_design,kill_criterion) VALUES (?,?,?,?)",
            (code, statement, test, kill))


def seed_demo(conn):
    if conn.execute("SELECT 1 FROM opportunities WHERE key LIKE 'demo-%' LIMIT 1").fetchone():
        return
    demo = [
        ("demo-posture-band-us", "[DEMO] Posture Band", "GiddyUp", "health/fitness", "US",
         3, 1, "white", 42.0, 22, 75, dict(trend_slope=0.8, creat_slope=0.15)),
        ("demo-pet-groom-kit-us", "[DEMO] Pet Grooming Kit", "GiddyUp", "pet", "US",
         2, 0, "white", 35.0, 48, 20, dict(trend_slope=-0.5, creat_slope=1.1)),
        ("demo-solar-lamp-eu", "[DEMO] Solar Lamp", "Altro network", "home", "EU",
         4, 1, "white", 28.0, 10, 90, dict(trend_slope=1.4, creat_slope=0.05)),
    ]
    src = conn.execute("SELECT id FROM sources WHERE name LIKE 'Osservazione%'").fetchone()["id"]
    sig_ids = {r["key"]: r["id"] for r in conn.execute("SELECT id,key FROM signals")}
    start = date.today() - timedelta(days=30)
    for key, name, network, vertical, geo, assets, prel, compl, payout, creat0, age0, p in demo:
        cur = conn.execute(
            "INSERT INTO opportunities(key,name,network,vertical,geo,assets_required,prelander_required,"
            "compliance_class,state,notes) VALUES (?,?,?,?,?,?,?,?, 'osservata', 'Dati sintetici dimostrativi — da eliminare quando arrivano dati reali.')",
            (key, name, network, vertical, geo, assets, prel, compl))
        oid = cur.lastrowid
        for i in range(31):
            d = (start + timedelta(days=i)).isoformat()
            rows = [
                ("payout_amount", payout + (0.5 if i > 20 and p["trend_slope"] > 1 else 0)),
                ("trend_index", max(1, min(100, 40 + p["trend_slope"] * i + 6 * math.sin(i / 3)))),
                ("creatives_active_count", max(1, creat0 + p["creat_slope"] * i + 2 * math.sin(i / 4))),
                ("creative_max_age_days", age0 + i),
                ("social_mentions_7d", max(0, 120 + p["trend_slope"] * 15 * i / 10 + 20 * math.sin(i / 2))),
            ]
            if i % 7 == 0:
                rows.append(("new_advertisers_14d", max(0, round(p["creat_slope"] * 6))))
            for skey, val in rows:
                conn.execute(
                    "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
                    "VALUES (?,?,?,?,?)", (oid, sig_ids[skey], round(val, 2), d, src))
    # previsioni demo: una risolta, una aperta
    opp = conn.execute("SELECT id FROM opportunities WHERE key='demo-solar-lamp-eu'").fetchone()["id"]
    conn.execute(
        "INSERT INTO predictions(opportunity_id,hypothesis_code,statement,probability,predictor,due_date,"
        "resolved,outcome,brier,resolved_at) VALUES (?,?,?,?,?,?,1,1,?,datetime('now'))",
        (opp, "A1", "[DEMO] Il numero di creativi attivi su Solar Lamp supererà 15 entro la scadenza.",
         0.7, "umano", (date.today() - timedelta(days=2)).isoformat(), (0.7 - 1) ** 2))
    conn.execute(
        "INSERT INTO predictions(opportunity_id,hypothesis_code,statement,probability,predictor,due_date) "
        "VALUES (?,?,?,?,?,?)",
        (opp, "A1", "[DEMO] Solar Lamp avrà ancora >5 advertiser attivi alla scadenza.",
         0.8, "sistema", (date.today() + timedelta(days=30)).isoformat()))


def main():
    init_db()
    conn = get_conn()
    seed_base(conn)
    if "--demo" in sys.argv:
        seed_demo(conn)
    conn.commit()
    conn.close()
    print("Seed completato." + (" (con dati demo)" if "--demo" in sys.argv else ""))


if __name__ == "__main__":
    main()
