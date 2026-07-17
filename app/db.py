"""Strato dati DOIM — SQLite, observations append-only per costruzione."""
import os
import pathlib
import sqlite3

DB_PATH = os.environ.get(
    "DOIM_DB", str(pathlib.Path(__file__).resolve().parent.parent / "doim.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    kind TEXT,
    access_mode TEXT,          -- 'api_ufficiale' | 'export_csv' | 'manuale' | 'scraping'
    tos_risk TEXT,             -- 'basso' | 'medio' | 'alto'
    status TEXT DEFAULT 'attiva'
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('A','B','C')),  -- A osservato, B stimato, C non conoscibile
    definition TEXT,
    UNIQUE (key, version)
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    network TEXT,
    vertical TEXT,
    geo TEXT,
    url TEXT,
    state TEXT NOT NULL DEFAULT 'rilevata'
        CHECK (state IN ('rilevata','osservata','qualificata','allocata','chiusa','morta')),
    approval_status TEXT NOT NULL DEFAULT 'da_richiedere'
        CHECK (approval_status IN ('da_richiedere','richiesta','approvata','rifiutata')),
    assets_required INTEGER,           -- proxy effort (B2)
    prelander_required INTEGER DEFAULT 0,
    compliance_class TEXT DEFAULT 'white'
        CHECK (compliance_class IN ('white','grey','black')),
    notes TEXT,
    first_seen TEXT DEFAULT (datetime('now'))
);

-- Append-only: registra QUANDO è accaduto (observed_at) e QUANDO lo abbiamo saputo (recorded_at).
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY,
    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
    signal_id INTEGER NOT NULL REFERENCES signals(id),
    value REAL,
    value_text TEXT,
    observed_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    source_id INTEGER REFERENCES sources(id)
);
CREATE INDEX IF NOT EXISTS idx_obs_opp_sig ON observations(opportunity_id, signal_id, observed_at);

CREATE TRIGGER IF NOT EXISTS obs_no_update BEFORE UPDATE ON observations
BEGIN SELECT RAISE(ABORT, 'observations è append-only: mai aggiornare, solo osservare di nuovo'); END;
CREATE TRIGGER IF NOT EXISTS obs_no_delete BEFORE DELETE ON observations
BEGIN SELECT RAISE(ABORT, 'observations è append-only: mai cancellare'); END;

CREATE TABLE IF NOT EXISTS hypotheses (
    code TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    test_design TEXT,
    kill_criterion TEXT,
    status TEXT NOT NULL DEFAULT 'aperta'
        CHECK (status IN ('aperta','in_test','confermata','falsificata','indecidibile')),
    verdict TEXT
);

-- Prediction journal: pre-registrata, con timestamp, verificata a scadenza (Brier).
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY,
    opportunity_id INTEGER REFERENCES opportunities(id),
    hypothesis_code TEXT REFERENCES hypotheses(code),
    statement TEXT NOT NULL,
    probability REAL NOT NULL CHECK (probability > 0 AND probability < 1),
    predictor TEXT NOT NULL DEFAULT 'umano' CHECK (predictor IN ('umano','sistema')),
    due_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved INTEGER NOT NULL DEFAULT 0,
    outcome INTEGER,
    brier REAL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY,
    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
    action TEXT NOT NULL CHECK (action IN ('alloca','controllo','scarta')),
    rationale TEXT,
    snapshot TEXT,             -- JSON dei segnali visibili AL MOMENTO della decisione (congelato)
    predicted_roi REAL,        -- previsione economica pre-registrata
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS outcomes (
    id INTEGER PRIMARY KEY,
    decision_id INTEGER UNIQUE NOT NULL REFERENCES decisions(id),
    spend REAL,
    revenue_network REAL,      -- ciò che dichiara il network (controparte, B4)
    revenue_tracked REAL,      -- ciò che misura il tracking proprio
    incidents TEXT,            -- ban, rejection creativi, cap raggiunti... (B8)
    censored INTEGER NOT NULL DEFAULT 0,  -- 1 = etichetta invalidata da incidente, non conta come fallimento
    measured_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Layer competitivo: singoli annunci osservati nelle ad library (Meta, TikTok, Google...).
-- Da qui si DERIVANO i segnali dell'opportunità (densità, longevità): non si digitano a mano.
CREATE TABLE IF NOT EXISTS creatives (
    id INTEGER PRIMARY KEY,
    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
    advertiser TEXT,           -- pagina/advertiser che pubblica l'annuncio
    ad_ref TEXT,               -- id o URL dell'annuncio nella library
    format TEXT,               -- image | video | carousel...
    landing_url TEXT,
    angle TEXT,                -- hook/angolo creativo (osservazione qualitativa)
    first_seen TEXT,           -- primo avvistamento (dalla library)
    last_seen TEXT,            -- ultimo avvistamento
    active INTEGER NOT NULL DEFAULT 1,
    source_id INTEGER REFERENCES sources(id),
    recorded_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_cre_opp ON creatives(opportunity_id, active);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def latest_observation(conn, opportunity_id, signal_key):
    return conn.execute(
        """SELECT o.value, o.value_text, o.observed_at FROM observations o
           JOIN signals s ON s.id = o.signal_id
           WHERE o.opportunity_id = ? AND s.key = ?
           ORDER BY o.observed_at DESC, o.id DESC LIMIT 1""",
        (opportunity_id, signal_key),
    ).fetchone()


def recompute_derived_signals(conn, opportunity_id, on_date=None):
    """Deriva i segnali dell'opportunità dai creativi osservati e li registra come
    osservazioni del giorno. Idempotente per data: non duplica lo snapshot se già esiste.
    Ritorna il dizionario dei valori scritti."""
    import datetime as _dt

    d = on_date or _dt.date.today().isoformat()
    cres = conn.execute(
        "SELECT advertiser, first_seen, last_seen, active FROM creatives WHERE opportunity_id=?",
        (opportunity_id,),
    ).fetchall()
    if not cres:
        return {}

    def _age(fs, ls, active):
        try:
            start = _dt.date.fromisoformat(str(fs)[:10])
        except (ValueError, TypeError):
            return None
        end = _dt.date.today() if active else (
            _dt.date.fromisoformat(str(ls)[:10]) if ls else _dt.date.today())
        return (end - start).days

    active = [c for c in cres if c["active"]]
    ages = [a for a in (_age(c["first_seen"], c["last_seen"], c["active"]) for c in active) if a is not None]
    recent_adv = set()
    for c in cres:
        try:
            fs = _dt.date.fromisoformat(str(c["first_seen"])[:10])
            if (_dt.date.today() - fs).days <= 14 and c["advertiser"]:
                recent_adv.add(c["advertiser"].strip().lower())
        except (ValueError, TypeError):
            continue

    values = {
        "creatives_active_count": float(len(active)),
        "creative_max_age_days": float(max(ages)) if ages else None,
        "new_advertisers_14d": float(len(recent_adv)),
    }
    src = conn.execute(
        "SELECT id FROM sources WHERE name LIKE 'Derivato%' LIMIT 1").fetchone()
    src_id = src["id"] if src else None
    written = {}
    for key, val in values.items():
        if val is None:
            continue
        sig = conn.execute(
            "SELECT id FROM signals WHERE key=? ORDER BY version DESC LIMIT 1", (key,)).fetchone()
        if not sig:
            continue
        # append-only: registra solo se il valore è CAMBIATO rispetto all'ultima osservazione
        # (evita duplicati inutili ma tiene aggiornato lo snapshot se i creativi cambiano in giornata)
        last = conn.execute(
            "SELECT value FROM observations WHERE opportunity_id=? AND signal_id=? "
            "ORDER BY observed_at DESC, id DESC LIMIT 1",
            (opportunity_id, sig["id"])).fetchone()
        if last is not None and last["value"] == val:
            continue
        conn.execute(
            "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
            "VALUES (?,?,?,?,?)", (opportunity_id, sig["id"], val, d, src_id))
        written[key] = val
    return written


def series(conn, opportunity_id, signal_key, limit=120):
    rows = conn.execute(
        """SELECT o.value, o.observed_at FROM observations o
           JOIN signals s ON s.id = o.signal_id
           WHERE o.opportunity_id = ? AND s.key = ? AND o.value IS NOT NULL
           ORDER BY o.observed_at DESC, o.id DESC LIMIT ?""",
        (opportunity_id, signal_key, limit),
    ).fetchall()
    return list(reversed(rows))
