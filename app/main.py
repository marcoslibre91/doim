"""DOIM — piattaforma interna di Decision Intelligence per il performance marketing.

MVP di ricerca (Fase 1): registro opportunità, observations append-only,
prediction journal con Brier score, registro ipotesi, decisioni con snapshot
congelato e outcome riconciliati (network vs tracking proprio).
"""
import csv
import io
import json
import pathlib
import re
from datetime import date, datetime, timezone
from urllib.parse import quote

from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from . import db
from .score import compute_profile, profile_summary

app = FastAPI(title="DOIM")
templates = Jinja2Templates(
    directory=str(pathlib.Path(__file__).resolve().parent / "templates")
)
db.init_db()


def today():
    return date.today().isoformat()


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "opp"


def unique_key(conn, base):
    key, i = base, 2
    while conn.execute("SELECT 1 FROM opportunities WHERE key=?", (key,)).fetchone():
        key = f"{base}-{i}"
        i += 1
    return key


def redirect(path, flash=None):
    if flash:
        sep = "&" if "?" in path else "?"
        path = f"{path}{sep}flash={quote(flash)}"
    return RedirectResponse(path, status_code=303)


def sparkline(rows, w=180, h=40):
    vals = [r["value"] for r in rows if r["value"] is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    pts = []
    for i, v in enumerate(vals):
        x = 2 + i * (w - 4) / (len(vals) - 1)
        y = h - 4 - (v - lo) / span * (h - 8)
        pts.append(f"{x:.1f},{y:.1f}")
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline fill="none" stroke="#4a7dcf" stroke-width="1.5" points="{" ".join(pts)}"/></svg>'
    )


def render(request, template, **ctx):
    ctx.setdefault("flash", request.query_params.get("flash"))
    return templates.TemplateResponse(request, template, ctx)


# ---------------------------------------------------------------- dashboard
STALE_DAYS = 3


@app.get("/")
def index(request: Request):
    conn = db.get_conn()

    # Azione: opportunità attive non osservate da troppo tempo (dati stantii, B7)
    tracked = conn.execute(
        "SELECT o.id, o.name, o.network, MAX(ob.observed_at) last_obs "
        "FROM opportunities o LEFT JOIN observations ob ON ob.opportunity_id=o.id "
        "WHERE o.state NOT IN ('morta','chiusa') GROUP BY o.id ORDER BY last_obs"
    ).fetchall()
    stale = []
    for r in tracked:
        if r["last_obs"] is None:
            stale.append({"opp": r, "days": None})
        else:
            age = (date.today() - date.fromisoformat(str(r["last_obs"])[:10])).days
            if age >= STALE_DAYS:
                stale.append({"opp": r, "days": age})

    # Azione: previsioni scadute da risolvere ora
    to_resolve = conn.execute(
        "SELECT p.*, o.name opp_name FROM predictions p LEFT JOIN opportunities o ON o.id=p.opportunity_id "
        "WHERE p.resolved=0 AND p.due_date <= date('now') ORDER BY p.due_date"
    ).fetchall()
    # Heads-up: previsioni in scadenza entro 7 giorni
    upcoming = conn.execute(
        "SELECT p.*, o.name opp_name FROM predictions p LEFT JOIN opportunities o ON o.id=p.opportunity_id "
        "WHERE p.resolved=0 AND p.due_date > date('now') AND p.due_date <= date('now','+7 day') ORDER BY p.due_date"
    ).fetchall()
    # Azione: decisioni allocate senza outcome registrato
    awaiting = conn.execute(
        "SELECT d.id, d.action, d.created_at, o.name opp_name, o.id opp_id FROM decisions d "
        "JOIN opportunities o ON o.id=d.opportunity_id "
        "LEFT JOIN outcomes oc ON oc.decision_id=d.id "
        "WHERE d.action IN ('alloca','controllo') AND oc.id IS NULL ORDER BY d.created_at"
    ).fetchall()
    # Nudge: previsioni pre-registrate negli ultimi 7 giorni (cadenza settimanale)
    preds_week = conn.execute(
        "SELECT COUNT(*) n FROM predictions WHERE created_at >= date('now','-7 day')"
    ).fetchone()["n"]

    counts = {
        "opps": conn.execute("SELECT COUNT(*) n FROM opportunities").fetchone()["n"],
        "obs": conn.execute("SELECT COUNT(*) n FROM observations").fetchone()["n"],
        "preds_open": conn.execute("SELECT COUNT(*) n FROM predictions WHERE resolved=0").fetchone()["n"],
        "hyp_open": conn.execute("SELECT COUNT(*) n FROM hypotheses WHERE status IN ('aperta','in_test')").fetchone()["n"],
    }
    cal = conn.execute(
        "SELECT predictor, COUNT(*) n, AVG(brier) brier FROM predictions WHERE resolved=1 GROUP BY predictor"
    ).fetchall()
    conn.close()
    n_actions = len(stale) + len(to_resolve) + len(awaiting) + (1 if preds_week == 0 else 0)
    return render(request, "index.html", stale=stale, to_resolve=to_resolve,
                  upcoming=upcoming, awaiting=awaiting, preds_week=preds_week,
                  counts=counts, cal=cal, n_actions=n_actions, stale_days=STALE_DAYS,
                  today=today())


@app.get("/help")
def help_page(request: Request):
    return render(request, "help.html")


# ------------------------------------------------------------ opportunities
@app.get("/opportunities")
def opportunities(request: Request):
    conn = db.get_conn()
    opps = conn.execute(
        "SELECT * FROM opportunities ORDER BY first_seen DESC"
    ).fetchall()
    enriched = []
    for o in opps:
        profile = compute_profile(conn, o)
        enriched.append({"opp": o, "profile": profile, "summary": profile_summary(profile)})
    conn.close()
    return render(request, "opportunities.html", items=enriched)


@app.post("/opportunities")
def add_opportunity(
    name: str = Form(...), network: str = Form(""), key: str = Form(""),
    vertical: str = Form(""), geo: str = Form(""), url: str = Form(""),
    assets_required: str = Form(""), prelander_required: str = Form("0"),
    compliance_class: str = Form("white"), notes: str = Form(""),
):
    conn = db.get_conn()
    base = slugify(key) if key.strip() else slugify(name)
    final_key = unique_key(conn, base)
    cur = conn.execute(
        "INSERT INTO opportunities(key,name,network,vertical,geo,url,assets_required,prelander_required,compliance_class,notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (final_key, name.strip(), network, vertical, geo, url,
         int(assets_required) if assets_required else None,
         int(prelander_required or 0), compliance_class, notes),
    )
    oid = cur.lastrowid
    conn.commit()
    conn.close()
    return redirect(f"/opportunities/{oid}",
                    flash=f"Opportunità «{name.strip()}» creata. Registra la prima osservazione qui sotto.")


@app.get("/opportunities/{oid}")
def opportunity_detail(request: Request, oid: int):
    conn = db.get_conn()
    opp = conn.execute("SELECT * FROM opportunities WHERE id=?", (oid,)).fetchone()
    if not opp:
        conn.close()
        return redirect("/opportunities")
    profile = compute_profile(conn, opp)
    summary = profile_summary(profile)
    signals = conn.execute("SELECT * FROM signals ORDER BY key").fetchall()
    charts = []
    for s in signals:
        rows = db.series(conn, oid, s["key"])
        if rows:
            charts.append({
                "signal": s, "svg": sparkline(rows), "n": len(rows),
                "last": rows[-1]["value"], "last_at": rows[-1]["observed_at"],
            })
    observations = conn.execute(
        "SELECT ob.*, s.key sig, s.tier, src.name src_name FROM observations ob "
        "JOIN signals s ON s.id=ob.signal_id LEFT JOIN sources src ON src.id=ob.source_id "
        "WHERE ob.opportunity_id=? ORDER BY ob.observed_at DESC LIMIT 60", (oid,)
    ).fetchall()
    predictions = conn.execute(
        "SELECT * FROM predictions WHERE opportunity_id=? ORDER BY created_at DESC", (oid,)
    ).fetchall()
    decisions = conn.execute(
        "SELECT d.*, oc.spend, oc.revenue_network, oc.revenue_tracked, oc.censored, oc.incidents "
        "FROM decisions d LEFT JOIN outcomes oc ON oc.decision_id=d.id "
        "WHERE d.opportunity_id=? ORDER BY d.created_at DESC", (oid,)
    ).fetchall()
    sources = conn.execute("SELECT * FROM sources ORDER BY name").fetchall()
    conn.close()
    return render(request, "opportunity.html", opp=opp, profile=profile, summary=summary,
                  charts=charts, observations=observations, predictions=predictions,
                  decisions=decisions, signals=signals, sources=sources, today=today())


@app.post("/opportunities/{oid}/state")
def set_state(oid: int, state: str = Form(...), approval_status: str = Form(...)):
    conn = db.get_conn()
    conn.execute("UPDATE opportunities SET state=?, approval_status=? WHERE id=?",
                 (state, approval_status, oid))
    conn.commit()
    conn.close()
    return redirect(f"/opportunities/{oid}", flash="Stato aggiornato.")


# ------------------------------------------------------------- observations
@app.post("/opportunities/{oid}/observations")
def add_observation(oid: int, signal_id: int = Form(...), value: str = Form(""),
                    value_text: str = Form(""), observed_at: str = Form(""),
                    source_id: str = Form("")):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO observations(opportunity_id,signal_id,value,value_text,observed_at,source_id) "
        "VALUES (?,?,?,?,?,?)",
        (oid, signal_id, float(value) if value else None, value_text or None,
         observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds"),
         int(source_id) if source_id else None),
    )
    conn.commit()
    conn.close()
    return redirect(f"/opportunities/{oid}", flash="Osservazione registrata.")


@app.get("/opportunities/{oid}/update")
def update_form(request: Request, oid: int):
    """Schermata di aggiornamento in blocco: tutti i segnali di un'opportunità in una volta."""
    conn = db.get_conn()
    opp = conn.execute("SELECT * FROM opportunities WHERE id=?", (oid,)).fetchone()
    if not opp:
        conn.close()
        return redirect("/opportunities")
    signals = conn.execute("SELECT * FROM signals ORDER BY tier, key").fetchall()
    rows = []
    for s in signals:
        last = db.latest_observation(conn, oid, s["key"])
        rows.append({"signal": s, "last": last})
    sources = conn.execute("SELECT * FROM sources ORDER BY name").fetchall()
    conn.close()
    return render(request, "update.html", opp=opp, rows=rows, sources=sources, today=today())


@app.post("/opportunities/{oid}/update")
async def update_submit(request: Request, oid: int):
    """Registra un'osservazione per ogni segnale in cui è stato inserito un valore."""
    form = await request.form()
    observed_at = (form.get("observed_at") or today()).strip()
    source_id = form.get("source_id") or ""
    conn = db.get_conn()
    n = 0
    for k, v in form.items():
        if not k.startswith("sig_") or v is None or str(v).strip() == "":
            continue
        try:
            sid = int(k[4:])
            val = float(v)
        except ValueError:
            continue
        conn.execute(
            "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
            "VALUES (?,?,?,?,?)",
            (oid, sid, val, observed_at, int(source_id) if source_id else None))
        n += 1
    if n and conn.execute("SELECT state FROM opportunities WHERE id=?", (oid,)).fetchone()["state"] == "rilevata":
        conn.execute("UPDATE opportunities SET state='osservata' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    msg = f"{n} osservazioni registrate." if n else "Nessun valore inserito."
    return redirect(f"/opportunities/{oid}", flash=msg)


@app.get("/import")
def import_page(request: Request):
    return render(request, "import.html")


@app.post("/import/csv")
async def import_csv(file: UploadFile):
    """CSV: opportunity_key,signal_key,value,observed_at,source"""
    text = (await file.read()).decode("utf-8", errors="replace")
    conn = db.get_conn()
    imported = skipped = 0
    for row in csv.DictReader(io.StringIO(text)):
        sig = conn.execute(
            "SELECT id FROM signals WHERE key=? ORDER BY version DESC LIMIT 1",
            ((row.get("signal_key") or "").strip(),),
        ).fetchone()
        if not sig:
            skipped += 1
            continue
        okey = (row.get("opportunity_key") or "").strip()
        opp = conn.execute("SELECT id FROM opportunities WHERE key=?", (okey,)).fetchone()
        if not opp:
            cur = conn.execute(
                "INSERT INTO opportunities(key,name) VALUES (?,?)", (okey, okey))
            opp_id = cur.lastrowid
        else:
            opp_id = opp["id"]
        src_name = (row.get("source") or "import_csv").strip()
        src = conn.execute("SELECT id FROM sources WHERE name=?", (src_name,)).fetchone()
        if not src:
            cur = conn.execute(
                "INSERT INTO sources(name,kind,access_mode,tos_risk) VALUES (?,?,?,?)",
                (src_name, "import", "export_csv", "basso"))
            src_id = cur.lastrowid
        else:
            src_id = src["id"]
        try:
            val = float(row["value"]) if row.get("value") else None
        except ValueError:
            val = None
        conn.execute(
            "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
            "VALUES (?,?,?,?,?)",
            (opp_id, sig["id"], val,
             (row.get("observed_at") or today()).strip(), src_id),
        )
        imported += 1
    conn.commit()
    conn.close()
    return redirect("/import",
                    flash=f"Import completato: {imported} osservazioni, {skipped} righe saltate.")


@app.post("/api/observations")
async def api_observations(request: Request):
    """Bulk JSON per connettori: [{opportunity_key, signal_key, value, observed_at, source}]"""
    payload = await request.json()
    conn = db.get_conn()
    imported = skipped = 0
    for row in payload:
        sig = conn.execute(
            "SELECT id FROM signals WHERE key=? ORDER BY version DESC LIMIT 1",
            (row.get("signal_key"),)).fetchone()
        opp = conn.execute(
            "SELECT id FROM opportunities WHERE key=?", (row.get("opportunity_key"),)).fetchone()
        if not sig or not opp:
            skipped += 1
            continue
        src_id = None
        if row.get("source"):
            src = conn.execute("SELECT id FROM sources WHERE name=?", (row["source"],)).fetchone()
            src_id = src["id"] if src else None
        conn.execute(
            "INSERT INTO observations(opportunity_id,signal_id,value,observed_at,source_id) "
            "VALUES (?,?,?,?,?)",
            (opp["id"], sig["id"], row.get("value"),
             row.get("observed_at") or today(), src_id))
        imported += 1
    conn.commit()
    conn.close()
    return JSONResponse({"imported": imported, "skipped": skipped})


# -------------------------------------------------------------- predictions
@app.get("/predictions")
def predictions(request: Request):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT p.*, o.name opp_name FROM predictions p "
        "LEFT JOIN opportunities o ON o.id=p.opportunity_id ORDER BY p.resolved, p.due_date"
    ).fetchall()
    cal = conn.execute(
        "SELECT predictor, COUNT(*) n, AVG(brier) brier, AVG(outcome) base_rate "
        "FROM predictions WHERE resolved=1 GROUP BY predictor").fetchall()
    opps = conn.execute("SELECT id,name FROM opportunities ORDER BY name").fetchall()
    conn.close()
    return render(request, "predictions.html", rows=rows, cal=cal, opps=opps, today=today())


@app.post("/predictions")
def add_prediction(statement: str = Form(...), probability: float = Form(...),
                   due_date: str = Form(...), predictor: str = Form("umano"),
                   opportunity_id: str = Form(""), hypothesis_code: str = Form("")):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO predictions(opportunity_id,hypothesis_code,statement,probability,predictor,due_date) "
        "VALUES (?,?,?,?,?,?)",
        (int(opportunity_id) if opportunity_id else None, hypothesis_code or None,
         statement, probability, predictor, due_date))
    conn.commit()
    conn.close()
    return redirect("/predictions", flash="Previsione pre-registrata.")


@app.post("/predictions/{pid}/resolve")
def resolve_prediction(pid: int, outcome: int = Form(...)):
    conn = db.get_conn()
    row = conn.execute("SELECT probability FROM predictions WHERE id=? AND resolved=0", (pid,)).fetchone()
    flash = "Previsione già risolta."
    if row:
        brier = (row["probability"] - outcome) ** 2
        conn.execute(
            "UPDATE predictions SET resolved=1, outcome=?, brier=?, resolved_at=datetime('now') WHERE id=?",
            (outcome, brier, pid))
        conn.commit()
        flash = f"Previsione risolta — Brier {brier:.3f}."
    conn.close()
    return redirect("/predictions", flash=flash)


# --------------------------------------------------------------- hypotheses
@app.get("/hypotheses")
def hypotheses(request: Request):
    conn = db.get_conn()
    rows = conn.execute("SELECT * FROM hypotheses ORDER BY code").fetchall()
    conn.close()
    return render(request, "hypotheses.html", rows=rows)


@app.post("/hypotheses/{code}/update")
def update_hypothesis(code: str, status: str = Form(...), verdict: str = Form("")):
    conn = db.get_conn()
    conn.execute("UPDATE hypotheses SET status=?, verdict=? WHERE code=?",
                 (status, verdict, code))
    conn.commit()
    conn.close()
    return redirect("/hypotheses", flash=f"Ipotesi {code} aggiornata.")


# ---------------------------------------------------------------- decisions
@app.get("/decisions")
def decisions(request: Request):
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT d.*, o.name opp_name, oc.spend, oc.revenue_network, oc.revenue_tracked, "
        "oc.censored, oc.incidents, oc.id outcome_id FROM decisions d "
        "JOIN opportunities o ON o.id=d.opportunity_id "
        "LEFT JOIN outcomes oc ON oc.decision_id=d.id ORDER BY d.created_at DESC"
    ).fetchall()
    enriched = []
    for r in rows:
        disc = None
        if r["revenue_tracked"] not in (None, 0) and r["revenue_network"] is not None:
            disc = (r["revenue_network"] - r["revenue_tracked"]) / r["revenue_tracked"] * 100
        roi = None
        if r["spend"] not in (None, 0) and r["revenue_tracked"] is not None:
            roi = (r["revenue_tracked"] - r["spend"]) / r["spend"] * 100
        enriched.append({"r": r, "disc": disc, "roi": roi})
    conn.close()
    return render(request, "decisions.html", rows=enriched)


@app.post("/opportunities/{oid}/decisions")
def add_decision(oid: int, action: str = Form(...), rationale: str = Form(""),
                 predicted_roi: str = Form("")):
    conn = db.get_conn()
    # Snapshot congelato: i segnali visibili ADESSO, per backtesting onesto (§7).
    sigs = conn.execute("SELECT id, key FROM signals").fetchall()
    snapshot = {}
    for s in sigs:
        row = db.latest_observation(conn, oid, s["key"])
        if row:
            snapshot[s["key"]] = {"value": row["value"], "observed_at": row["observed_at"]}
    conn.execute(
        "INSERT INTO decisions(opportunity_id,action,rationale,snapshot,predicted_roi) "
        "VALUES (?,?,?,?,?)",
        (oid, action, rationale, json.dumps(snapshot),
         float(predicted_roi) if predicted_roi else None))
    if action == "alloca":
        conn.execute("UPDATE opportunities SET state='allocata' WHERE id=?", (oid,))
    conn.commit()
    conn.close()
    return redirect(f"/opportunities/{oid}",
                    flash=f"Decisione «{action}» registrata con snapshot dei segnali congelato.")


@app.post("/decisions/{did}/outcome")
def add_outcome(did: int, spend: float = Form(...), revenue_network: str = Form(""),
                revenue_tracked: str = Form(""), incidents: str = Form(""),
                censored: str = Form("0")):
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO outcomes(decision_id,spend,revenue_network,revenue_tracked,incidents,censored) "
        "VALUES (?,?,?,?,?,?) ON CONFLICT(decision_id) DO UPDATE SET "
        "spend=excluded.spend, revenue_network=excluded.revenue_network, "
        "revenue_tracked=excluded.revenue_tracked, incidents=excluded.incidents, "
        "censored=excluded.censored, measured_at=datetime('now')",
        (did, spend, float(revenue_network) if revenue_network else None,
         float(revenue_tracked) if revenue_tracked else None,
         incidents or None, int(censored or 0)))
    conn.commit()
    conn.close()
    return redirect("/decisions", flash="Outcome registrato.")
