# DOIM — Decision Intelligence per il Performance Marketing

Piattaforma **interna di ricerca** per rispondere a una sola domanda: *su quale opportunità
conviene investire tempo e capitale oggi?* — con la disciplina descritta in
[`ANALISI_COMITATO_INVESTIMENTO.md`](ANALISI_COMITATO_INVESTIMENTO.md).

Questo MVP è lo strumento della **Fase 1 (ricerca)**: non predice niente, e lo dichiara.
Serve a costruire le tre cose che contano — osservazioni storicizzate, previsioni
pre-registrate, etichette decisione→outcome — prima di qualsiasi modello.

## Avvio rapido

```bash
pip install -r requirements.txt
python -m app.seed --demo        # fonti, segnali, ipotesi A1-A13 (+ 3 opportunità demo)
uvicorn app.main:app --port 8000
# → http://localhost:8000
```

Senza `--demo` il seed carica solo fonti, segnali e registro ipotesi (partenza pulita).
Il database è un singolo file SQLite (`doim.db`) — backup = copia del file.

## Cosa c'è dentro (e perché)

| Modulo | Cosa fa | Principio dell'analisi |
|---|---|---|
| **Opportunità** | registro con ciclo di vita (rilevata → … → morta), stato approvazione, proxy effort, classe compliance | §7, B1, B2, B9 |
| **Osservazioni** | append-only per trigger SQL (non si aggiornano né cancellano), con doppio tempo *observed_at / recorded_at*, fonte e tier A/B | §7 (bitemporalità), §8 |
| **Profilo per componenti** | Domanda / Concorrenza / Economics / Durabilità / Fit / Data confidence — ogni semaforo mostra gli input grezzi e dichiara i propri limiti. **Niente punteggio unico**: vietato prima delle etichette | §10 |
| **Prediction journal** | previsioni pre-registrate con probabilità e scadenza, risoluzione manuale, Brier score, calibrazione sistema vs umano | §7.1, M1, A10 |
| **Decisioni** | alloca / **controllo** (casuale) / scarta, con ROI previsto pre-registrato e **snapshot congelato** dei segnali visibili al momento — il backtesting non può barare | §7, Q3 del piano |
| **Outcome** | spend, revenue *dichiarato dal network* E revenue *dal tracking proprio* (discrepanza = trust del network), incidenti, censura delle etichette contaminate | B4, B8 |
| **Registro ipotesi** | A1–A13 pre-caricate con test e kill criterion; stati aperta/in test/confermata/falsificata | regola d'oro |
| **Import** | CSV (`opportunity_key, signal_key, value, observed_at, source`) + API bulk `POST /api/observations` | — |

## Collegare GiddyUp e gli altri network

GiddyUp (e diversi network usati dagli affiliati pro) gira su **Everflow**: dal pannello
affiliato puoi generare una API key personale. `app/connectors.py` scarica le offerte
visibili al tuo account e registra i payout come osservazioni:

```bash
export EVERFLOW_API_KEY=...   # dal pannello del network
python -m app.connectors
```

Confine d'uso deliberato: **solo i dati del proprio account, via API ufficiale** — è la
strategia "fonti con diritto d'accesso stabile" (ipotesi A4), non scraping. Per i network
senza API: esporta i report CSV dal pannello e importali dalla pagina *Import dati*.
Dati da fonti manuali (Ad Library, Trends) si registrano in 10 secondi dalla pagina
dell'opportunità.

## La routine che rende utile lo strumento

1. **Ogni giorno/2 giorni** (10 min): aggiorna le osservazioni delle opportunità in tracking
   (connettore + 2-3 letture manuali da Ad Library/Trends).
2. **Ogni settimana** (15 min): pre-registra 3-5 previsioni nel journal — anche a puro intuito.
   È il track record, non la pipeline, che vale (M1).
3. **A ogni scadenza**: risolvi le previsioni (vero/falso). Il Brier si calcola da solo.
4. **A ogni lancio**: registra la decisione PRIMA di lanciare (snapshot + ROI previsto);
   registra l'outcome con entrambe le revenue (network e tracking). Ogni 3-4 allocazioni
   scelte da te, una di **controllo** scelta a caso tra le ammissibili.
5. **Ogni mese**: aggiorna il Registro ipotesi con l'evidenza accumulata.

## Cosa manca di proposito

Scraping automatico multi-fonte, knowledge graph, score composito, modelli predittivi,
multi-utente. Sono vietati dalla regola d'oro finché le ipotesi non maturano:
*nessuna riga di infrastruttura che non serva a falsificare un'ipotesi numerata.*
