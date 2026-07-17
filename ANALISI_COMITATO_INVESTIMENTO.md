# Comitato di Investimento — Analisi Adversariale
## Piattaforma di Decision Intelligence per il Performance Marketing ("DOIM")

**Data:** 2026-07-17
**Mandato:** decidere se questa idea merita $20M. L'obiettivo del comitato non è confermarla: è distruggerla. Ciò che sopravvive, si costruisce.

**Convenzioni usate in tutto il documento:**
- **[FATTO]** — verificabile oggi, senza costruire nulla.
- **[IPOTESI]** — plausibile ma non dimostrato. Va trattato come falso finché non validato.
- **[NON CONOSCIBILE]** — informazione strutturalmente inaccessibile. Nessun modello la recupera.

---

## 1. Riscrittura dell'idea (come si presenterebbe a un fondo)

> **Tesi.** Il performance marketing è un mercato di allocazione di capitale travestito da mestiere creativo. Ogni giorno migliaia di operatori decidono dove mettere tempo e budget — quale offerta, quale nicchia, quale canale — basandosi su intuizione, screenshot e rumore. Non esiste un registro storico delle "opportunità digitali": nascono, si saturano e muoiono senza lasciare traccia strutturata.
>
> **Prodotto.** Costruiamo il registro. Un sistema che identifica ogni opportunità monetizzabile (un'offerta su un network affiliativo, un prodotto emergente, una nicchia pubblicitaria), la tratta come uno strumento finanziario con un ticker, e ne registra quotidianamente lo stato: segnali di domanda, pressione competitiva, economics dichiarati, longevità dei creativi che la promuovono. Non lo stato attuale — l'intera serie storica.
>
> **Il vero prodotto non è il dato: è l'etichetta.** Chiunque può raccogliere segnali. Nessuno possiede il *risultato* delle decisioni prese su quei segnali. Noi operiamo capitale proprio sulle opportunità selezionate dal sistema, e ogni allocazione produce un'etichetta di verità (outcome economico reale) che nessun concorrente può replicare, comprare o scrapare. Il ciclo osserva → decide → alloca → misura → aggiorna è il motore che trasforma un dataset in un vantaggio.
>
> **Sequenza.** Fase 1: uso interno come veicolo di ricerca — validare quali indicatori sono predittivi e quali no, con disciplina da fondo quantitativo (pre-registrazione delle previsioni, baseline casuali, out-of-sample). Fase 2: solo se la predittività è dimostrata, decidere il modello di monetizzazione — operatore proprietario (prop), dati (terminal), o prodotto.

**Nota del comitato sulla riscrittura:** questa è la versione più forte e più onesta dell'idea. Notare cosa abbiamo *tolto*: "decine di fonti", "centinaia di indicatori", "AI". Sono costi, non tesi. La tesi è una sola: *le etichette di outcome proprietarie battono i segnali pubblici*. Se questa frase è falsa, tutto il resto è un aggregatore di API con ambizioni.

---

## 2. Debolezze — tutte

### 2.1 Tecniche

1. **Accesso ai dati precario per costruzione.** Le fonti elencate (affiliate network, ad libraries, social) o vietano esplicitamente la raccolta sistematica nei ToS, o offrono API con rate limit e revoca unilaterale. Un sistema il cui asset è "serie storiche lunghe" costruito su fonti che possono chiudersi domani ha una fondazione contraddittoria: il valore cresce col tempo, il rischio di interruzione pure. **[FATTO]**: Meta, TikTok e i principali network hanno storicamente ristretto accessi senza preavviso (CrowdTangle chiuso nel 2024 è il precedente canonico).
2. **Entity resolution è il problema vero, non l'acquisizione.** "La stessa opportunità" appare come offerta su CJ, prodotto su Whop, advertiser nella Meta Ad Library, hashtag su TikTok — con nomi, ID e granularità diversi. Collegarle è un problema di record linkage sporco, continuo, mai finito. Chi sottovaluta questo costruisce dieci silos, non un registro. È qui che muore la maggior parte dei progetti simili. **[FATTO]** per esperienza di settore.
3. **Schema drift permanente.** Ogni fonte cambia formato, semantica e disponibilità dei campi. Una serie storica di 3 anni con 5 cambi di definizione non è una serie storica: è un artefatto. Serve versioning semantico dei segnali dal giorno zero.
4. **Survivorship bias nella raccolta.** Se il crawler scopre le opportunità quando diventano visibili (cioè quando già funzionano), il database contiene solo vincitori osservati tardi. Le serie storiche partiranno sistematicamente dopo la fase in cui la decisione era più preziosa.

### 2.2 Statistiche (le più gravi)

5. **Multiple hypothesis testing garantito.** "Centinaia di indicatori al giorno" testati contro pochi outcome produce correlazioni spurie con certezza matematica, non con rischio. Con 300 indicatori e soglia p<0.05, ~15 falsi positivi attesi *per ogni test battery*. Senza pre-registrazione e correzione, il sistema "scoprirà" KPI predittivi che non esistono. Questa è la modalità di fallimento più probabile dell'intero progetto.
6. **Il feedback loop è affamato per costruzione.** Il sistema "impara dai risultati", ma i risultati arrivano solo dalle opportunità su cui si alloca davvero. Un operatore singolo esegue forse 5–20 allocazioni serie l'anno. Con N=20 etichette e 300 feature, non si addestra nulla: si raccontano storie. Il collo di bottiglia del machine learning qui non è il modello né i dati osservazionali — è la *capacità di esecuzione* che genera etichette.
7. **Selection bias sulle etichette.** Si osserva l'outcome solo delle opportunità scelte. Il controfattuale ("cosa sarebbe successo su quelle scartate?") non esiste. Senza allocazioni di controllo (anche piccole, anche casuali), il "learning" confonde qualità del segnale con qualità dell'esecuzione dell'operatore.
8. **Non-stazionarietà e riflessività.** I mercati finanziari sono riflessivi ma liquidi; questo mercato è riflessivo e *illiquido e minuscolo per singola opportunità*. Un'opportunità affiliate ha capienza limitata: se il segnale è vero e altri lo vedono, si satura in settimane. L'alpha qui decade più velocemente che in finanza, e non esiste lo short: non si può monetizzare la previsione "questa opportunità morirà". Metà dello spazio predittivo è inutilizzabile.
9. **Regime change esogeni.** Un cambio di algoritmo Meta/TikTok/Google, o di policy di un network, invalida anni di storico in un giorno. Il valore composto della serie storica — l'asset dichiarato — è condizionato a regimi stabili che notoriamente non lo sono.
10. **Attribution dell'outcome.** "Questa opportunità ha reso X" dipende da creativo, timing, budget, skill dell'operatore. Separare il contributo dell'*opportunità* da quello dell'*esecuzione* è un problema di attribuzione causale che il piano non menziona nemmeno.

### 2.3 Di prodotto

11. **Per anni non c'è prodotto.** Uso interno = zero ricavi, zero validazione di mercato, zero pressione evolutiva esterna. È una scelta legittima (è ricerca), ma va chiamata col suo nome: non è una startup in questa fase, è un progetto di R&S autofinanziato.
12. **Utente singolo = overfitting di prodotto.** Un sistema costruito attorno alle decisioni di una persona codifica i bias di quella persona. Il giorno in cui si espone a terzi, si scopre che "la decisione" di altri operatori ha vincoli diversi (verticali, geografie, capitale, avversione al rischio).

### 2.4 Economiche

13. **Il valore della decisione ha un tetto basso.** Migliorare la selezione di opportunità affiliate vale, per un operatore medio, migliaia — non milioni — di euro l'anno. Il valore aggregato esiste solo (a) operando capitale proprio a scala, o (b) vendendo a molti. Il piano rimanda entrambe.
14. **Costo di mantenimento sottostimato.** Pipeline su decine di fonti ostili = manutenzione perpetua. Il costo non è costruire il crawler: è tenerlo vivo per 5 anni mentre le fonti combattono attivamente. Stima onesta: 1–2 ingegneri full-time solo per la sopravvivenza delle pipeline, prima di qualsiasi ricerca.
15. **Se commercializzato: mercato churn-heavy e price-sensitive.** Gli acquirenti (affiliati, media buyer) sono notoriamente tra i peggiori clienti SaaS: alta mortalità professionale, condivisione account, disponibilità a pagare bassa e volatile.

### 2.5 Competitive

16. **Il layer osservazionale è già un mercato affollato.** Similarweb, Semrush, Sensor Tower/data.ai, SpyFu, AdBeat, PiPiAds, Minea, WinningHunter, Foreplay, i tool di "product research" dropshipping. Tutti vendono segnali su "cosa sta funzionando". Se il progetto compete sul layer dei segnali, è morto in partenza contro operatori con 10 anni di panel data.
17. **I segnali pubblici sono, per definizione, già arbitrati.** Se un indicatore ricavabile dalla Meta Ad Library fosse fortemente predittivo, migliaia di media buyer che la guardano ogni giorno lo starebbero già sfruttando. L'edge, se esiste, sta nella *combinazione longitudinale + etichette*, non nei segnali singoli. **[IPOTESI]** da validare, non da assumere.

### 2.6 Legali

18. **ToS delle fonti.** Quasi tutti i network affiliativi vietano contrattualmente ridistribuzione e uso derivato dei dati delle offerte. Lo scraping di piattaforme social vive in una zona grigia (giurisprudenza hiQ/LinkedIn favorevole ai dati pubblici negli USA, ma Meta e altri fanno enforcement aggressivo via ban e cause contrattuali). Uso interno riduce il rischio; commercializzazione lo moltiplica — e il piano prevede proprio la commercializzazione futura.
19. **GDPR.** Se tra i segnali entrano dati di creator/community riconducibili a persone fisiche, si applica il GDPR anche per uso interno (base giuridica, minimizzazione, diritto di opposizione). "Sono dati pubblici" non è una base giuridica.
20. **Diritto sui generis sulle banche dati (UE).** Estrarre sistematicamente porzioni sostanziali di database altrui è violazione autonoma in Europa, indipendentemente dal copyright sui singoli dati.

### 2.7 Architetturali

21. **Il paradosso della scala: questi sono small data.** Centinaia di indicatori × decine di migliaia di opportunità × osservazione giornaliera = qualche GB l'anno. Buona notizia per i costi; pessima per il moat: "abbiamo tanti dati" non sarà mai vero. Qualsiasi difendibilità deve venire da *ciò che non si può ricomprare* (il tempo trascorso e le etichette), non dal volume.
22. **Il rischio architetturale principale è costruire troppo.** Knowledge graph, decision engine, scoring — prima di sapere se un solo indicatore è predittivo. La direzione sbagliata classica: infrastruttura prima dell'evidenza. (Vedi §11: il primo anno è ricerca con strumenti minimi, non piattaforma.)

**Dove il piano è debole, due alternative per ciascun punto critico:**

- *Feedback loop affamato (punto 6):* (a) consorzio di operatori che condividono outcome anonimizzati in cambio di accesso al sistema — moltiplica le etichette di 10–50×; (b) ridurre l'ambizione da "predire il successo" a "predire eventi osservabili pubblicamente" (saturazione, mortalità di un'offerta), dove le etichette sono gratuite e abbondanti perché derivano dall'osservazione stessa.
- *Accesso dati precario (punto 1):* (a) privilegiare fonti con diritto d'accesso stabile (DSA transparency database UE per le ad libraries — obbligo di legge, non concessione; dati propri dei network dove si è affiliati attivi con account legittimo); (b) strategia "few sources deep": 2–3 fonti difendibili e complete invece di 20 fragili.
- *Tetto economico basso (punto 13):* (a) modello prop a scala — team di operatori che eseguono, il sistema decide l'allocazione; (b) verticale B2B diverso: vendere l'intelligence a chi ha capienza grande (brand che scelgono network/partner, non affiliati che scelgono offerte).

---

## 3. Assunzioni implicite (ogni "probabilmente/potrebbe/forse" reso esplicito)

Il pitch originale contiene, nascoste, almeno queste ipotesi. Ognuna è falsificabile e va trattata come falsa finché non dimostrata:

| # | Assunzione implicita | Stato | Come falsificarla |
|---|---|---|---|
| A1 | Esistono segnali osservabili pubblicamente che precedono il successo economico di un'opportunità | [IPOTESI] | Studio retrospettivo + previsioni pre-registrate out-of-sample (§11) |
| A2 | Il vantaggio temporale del segnale è abbastanza lungo da poter agire prima della saturazione | [IPOTESI] | Misurare lag segnale→saturazione su coorti storiche |
| A3 | La serie storica ha valore composto (più storico ⇒ decisioni migliori) | [IPOTESI] | Confrontare accuratezza predittiva con finestre 3/6/12 mesi: se plateau a 3 mesi, l'asset "storico" non compone |
| A4 | Le fonti resteranno accessibili a costo sostenibile per anni | [IPOTESI] | Audit legale/tecnico fonte per fonte, con piano B per ognuna |
| A5 | Le opportunità sono confrontabili tra loro (una metrica comune ha senso cross-verticale) | [IPOTESI] | Verificare se i predittori sono stabili tra verticali o completamente idiosincratici |
| A6 | L'outcome di un'allocazione misura la qualità dell'opportunità (e non solo dell'esecuzione) | [IPOTESI] | Allocazioni ripetute su stessa opportunità con esecuzioni diverse; controlli |
| A7 | Il numero di allocazioni interne genererà etichette sufficienti per "imparare" | [IPOTESI] — quasi certamente falsa per un singolo operatore | Contare: quante etichette/anno realisticamente? Se <100, ridisegnare (§2, alternative) |
| A8 | I segnali pubblici non sono già completamente arbitrati da chi li guarda ogni giorno | [IPOTESI] | Se A1 regge out-of-sample, A8 regge; sono la stessa domanda |
| A9 | "Imparare dai risultati" è possibile nonostante regime change delle piattaforme | [IPOTESI] | Test di stabilità temporale dei predittori attraverso eventi noti (update algoritmi) |
| A10 | Il sistema battera l'intuizione dell'operatore esperto (altrimenti a cosa serve?) | [IPOTESI] | Torneo: decisioni del sistema vs decisioni umane vs selezione casuale, stesso capitale |
| A11 | Ci sarà un mercato disposto a pagare, se si commercializza | [IPOTESI] | Rinviabile: irrilevante finché A1 non è dimostrata |
| A12 | I dati raccolti oggi con definizioni di oggi saranno interpretabili tra 3 anni | [IPOTESI] | Dipende da disciplina di versioning (§7); è una scelta, non un fatto |

**L'ipotesi madre è A1.** Se A1 è falsa, il progetto è un data warehouse costoso. Tutto il piano di ricerca (§11) esiste per attaccare A1 prima di ogni altra cosa.

---

## 4. Il vero vantaggio competitivo

Escludiamo esplicitamente, come richiesto: AI (commodity), API (commodity), dashboard (commodity), UX (copiabile in un trimestre). Escludiamo anche due candidati che sembrano moat e non lo sono:

- **"Il database proprietario dei segnali"** — no. I segnali provengono da fonti pubbliche o semi-pubbliche: chiunque con 18 mesi e due ingegneri ricostruisce il layer osservazionale. Similarweb e Semrush l'hanno già fatto meglio.
- **"Le serie temporali lunghe"** — parzialmente. Il tempo non si compra (nessuno può backfillare il 2026 nel 2028), quindi c'è un vantaggio da first-mover *sul proprio archivio*. Ma vale solo se A3 regge — se la predittività non migliora con la profondità dello storico, l'archivio è zavorra.

Il vantaggio difendibile, se esiste, è uno solo, con due componenti:

**Il dataset decisione→outcome, e il registro delle ipotesi falsificate.**

1. **Etichette di outcome proprietarie.** Il risultato economico reale delle allocazioni fatte sulle opportunità osservate. Nessun concorrente lo possiede perché nessun vendor di tool *opera capitale*: Similarweb vende segnali, non conosce il P&L di chi li usa. Questo dato non è scrapabile, non è comprabile, ed è l'unico che permette di rispondere alla domanda del prodotto ("dove conviene investire?") invece che alla domanda dei competitor ("cosa sta succedendo?"). *Vincolo brutale:* vale solo a volume — da qui la necessità strutturale del consorzio o della scala operativa (§2, alternativa al punto 6).
2. **La conoscenza negativa.** Il registro di quali indicatori NON sono predittivi, con evidenza. È l'asset di Renaissance che nessuno vede: sapere cosa ignorare. Non appare in nessuna demo, non si copia guardando il prodotto, e fa risparmiare a chi lo possiede anni di vicoli ciechi.

Tutto il resto — pipeline, graph, scoring — è costo d'ingresso, non vantaggio.

---

## 5. Il vero asset dopo cinque anni

Scenario di successo (condizionato ad A1, A3, A7):

1. **Il libro mastro etichettato:** N migliaia di cicli di vita completi di opportunità (nascita → crescita → saturazione → morte) con, per un sottoinsieme, l'outcome economico di allocazioni reali. È l'equivalente di un *loan book* per il credit scoring: il dato che trasforma un modello da accademico a industriale.
2. **Priori calibrati per verticale:** distribuzioni empiriche ("le offerte SaaS su PartnerStack con payout crescente sopravvivono mediamente X mesi; il tasso di falsi segnali del pattern Y è Z%") — conoscenza attuariale del settore che oggi non esiste da nessuna parte.
3. **Il registro delle ipotesi:** centinaia di ipotesi testate, quasi tutte falsificate, con metodo documentato.
4. **Opzionalità sul modello di business:** con 1–3 si può diventare (a) operatore prop a scala, (b) fondo/holding che alloca su opportunità digitali, (c) data business stile terminal, (d) underwriter (il "credit bureau" delle opportunità digitali — chi presta o anticipa capitale ad affiliati/creator avrebbe bisogno esattamente di questo). L'opzione (d) è quella che nessun competitor attuale può esercitare.

Scenario onesto alternativo: se A1 regge debolmente e A9 no (predittività reale ma instabile tra regimi), l'asset a 5 anni è *il team e il metodo*, monetizzabile solo come operatore, mai come prodotto. Se A1 non regge, l'asset a 5 anni è un archivio ben ordinato di rumore.

---

## 6. Analogie — a cosa somiglia davvero

| Riferimento | Somiglianza | Perché l'analogia regge / crolla |
|---|---|---|
| **Renaissance Technologies** | ★★★★ (intento) | È l'analogia dell'*intento*: segnali proprietari, uso interno, rifiuto di vendere l'edge, disciplina statistica, "imparare dai risultati". Crolla sull'ambiente: RenTec opera su mercati liquidi, con short, migliaia di trade/giorno (etichette abbondanti), costi di transazione noti. Qui: mercato illiquido, no short, decine di "trade" l'anno, outcome contaminati dall'esecuzione. La disciplina va importata; l'economia del modello no. |
| **Similarweb / Semrush** | ★★★★ (meccanica) | È l'analogia della *meccanica dati*: stimare grandezze non osservabili (traffico, spend) da segnali indiretti, vendere il delta informativo. È anche lo specchio del rischio: se il progetto si ferma al layer osservazionale, *diventa* un piccolo Semrush in un mercato dove Semrush esiste già. |
| **Bloomberg** | ★★ | Regge solo nello scenario di commercializzazione a 5+ anni: standard informativo di un'asset class (le opportunità digitali come strumenti con ticker e storico). Crolla oggi: Bloomberg vive di dati *forniti volontariamente* da chi ha interesse a essere visto (exchange, dealer). Qui le fonti sono ostili. Bloomberg è una destinazione possibile, non un modello operativo. |
| **Nielsen** | ★★ | Regge come ambizione di "measurement standard" (la verità terza su cosa funziona). Crolla perché Nielsen vende a chi compra media a miliardi; qui i compratori sono frammentati e piccoli. |
| **Palantir** | ★ | Non regge. Palantir è servizi di integrazione dati su dati *del cliente*. Qui i dati sono propri e il deployment non esiste. Da scartare come riferimento. |
| **Zillow (Zestimate) — aggiunta del comitato** | ★★★ | Analogia non richiesta ma istruttiva in negativo: Zillow aveva il miglior modello di stima del settore e ha perso $500M+ quando ha iniziato ad *allocare capitale proprio* sulle proprie stime (Zillow Offers). Morale: un modello buono per stimare non è automaticamente buono per decidere quando entri l'esecuzione. È l'avvertimento esatto per la fase prop di questo progetto. |

**Sintesi:** ambizione alla Renaissance, meccanica dati alla Similarweb, rischio di fallimento alla Zillow. Il progetto vive nello spazio tra la prima e la seconda: se scivola sulla seconda, non ha ragione d'esistere; se pretende la prima senza le etichette, si illude.

---

## 7. Framework teorico del sistema (concetti, zero codice)

Il principio ordinatore: **separazione rigida tra ciò che è osservato, ciò che è stimato, ciò che è creduto e ciò che è deciso.** Ogni strato può sbagliare in modo diverso e deve essere auditabile separatamente.

### Entità

- **Source** — una fonte dati, con contratto semantico versionato e stato di salute. Le fonti muoiono: è un'entità di prima classe, non una configurazione.
- **Signal** — una grandezza osservabile definita *indipendentemente dalla fonte* (es. "numero di advertiser attivi che promuovono X"), con definizione versionata. Quando la definizione cambia, nasce una nuova versione: mai sovrascrivere la semantica.
- **Observation** — un evento immutabile e append-only: (signal, entità, valore, istante, fonte, versione). Il sistema non "aggiorna" mai: osserva. Tutta la storia deriva da qui. Include il *quando lo abbiamo saputo* oltre al *quando è accaduto* (bitemporalità concettuale): indispensabile per backtesting onesto, altrimenti ogni test retrospettivo bara con informazione futura.
- **Opportunity** — l'entità centrale: un'occasione di allocazione identificata e risolta attraverso le fonti (il lavoro di entity resolution del §2.1.2 vive qui). Ha un ciclo di vita esplicito a stati: *rilevata → osservata → qualificata → allocata → chiusa/morta*, con transizioni datate.
- **Hypothesis** — un'affermazione falsificabile su una relazione segnale→esito, con: enunciato, predizione pre-registrata, finestra di validità, esito del test. Cittadino di prima classe: il registro delle ipotesi È il prodotto della fase di ricerca.
- **Decision** — l'atto di allocare (o esplicitamente non allocare) su un'Opportunity, con: razionale, segnali visibili *al momento della decisione* (snapshot congelato), previsione quantitativa pre-registrata.
- **Outcome** — il risultato economico misurato di una Decision, con la sua incertezza di attribuzione dichiarata.

### Relazioni (il knowledge graph, e i suoi limiti)

Le opportunità non sono indipendenti: condividono network, verticali, advertiser, creator, meccaniche. Il grafo serve a tre cose precise: (a) propagare segnali (un network che degrada i payout tocca tutte le sue offerte), (b) trovare comparabili storici ("opportunità simili a questa, come sono finite?"), (c) rilevare contagio/saturazione tra opportunità vicine. **Critica preventiva:** un knowledge graph senza casi d'uso definiti è il buco nero classico dell'ingegneria di questi progetti. Nel primo anno bastano relazioni tabellari; il grafo si costruisce quando (a)-(c) sono domande frequenti, non prima.

### Serie temporali

Ogni coppia (Opportunity, Signal) è una serie. Le decisioni non guardano valori: guardano *forme* — livello, derivata, accelerazione, volatilità, età dell'opportunità, posizione nel ciclo di vita. Il confronto è sempre contro coorti di comparabili storici, mai contro soglie assolute (una crescita del 40% significa cose opposte in un verticale nascente e in uno saturo).

### Feedback loop (i tre anelli, da non confondere)

1. **Anello di calibrazione (settimane):** previsione pre-registrata vs realtà osservata → punteggio di calibrazione (es. Brier) per ipotesi e per decisore. Funziona anche senza allocare: si può prevedere la sopravvivenza di opportunità *non* scelte e verificarla osservando. È l'anello che genera etichette gratis e abbondanti — la risposta principale al problema A7.
2. **Anello di allocazione (mesi):** Decision → Outcome → aggiornamento dei priori. Lento, costoso, contaminato dall'esecuzione — ma è l'unico che misura ciò che conta davvero.
3. **Anello di regime (anni):** monitoraggio della stabilità dei predittori nel tempo; quando un predittore validato smette di funzionare, l'evento va registrato come dato (è informazione sul regime), non silenziosamente riassorbito.

### Decision engine

Nell'ordine di maturità, e mai saltando stadi: (1) *filtro* — esclude l'inammissibile con regole esplicite; (2) *ranking* — ordina per comparabilità con successi storici, con motivazione visibile per componente (§10); (3) *raccomandazione con previsione* — ogni suggerimento accompagnato da una predizione falsificabile e dalla sua incertezza. Mai automazione dell'allocazione nel perimetro di questo piano. Il motore propone; l'umano decide; il sistema registra entrambi e il disaccordo tra i due è esso stesso un segnale tracciato (serve per A10).

---

## 8. Tassonomia dei dati

### A. Osservabili direttamente [FATTI, al netto di errori di misura]

- Esistenza, metadati e condizioni dichiarate delle offerte sui network (payout, commission rate, EPC dichiarato dal network, cookie duration) — *dichiarati, non verificati: osservabile è l'annuncio, non la sua verità*.
- Presenza/assenza di annunci nelle ad libraries; numero di creativi attivi per advertiser; data di primo/ultimo avvistamento di un creativo (⇒ longevità osservata).
- Metriche pubbliche social: view, like, crescita follower, frequenza di pubblicazione, volume di menzioni.
- Trend di ricerca (Google Trends e simili) — indici relativi, non volumi.
- Attività pubblica di community (post, thread, sentiment testuale su forum/subreddit/Discord pubblici).
- Prezzi pubblici, posizionamenti marketplace, recensioni, ranking.
- **I propri dati operativi:** spend, revenue, EPC reale, conversion rate delle proprie allocazioni. L'unico blocco di verità assoluta del sistema.

### B. Stimabili [modelli, con errore non eliminabile — ogni stima deve viaggiare col suo intervallo]

- Spesa pubblicitaria altrui (da numero creativi × longevità × reach visibile — errore ampio).
- Traffico di siti/landing terzi (il mestiere di Similarweb: errori del 30–300% sui siti piccoli, documentato).
- Grado di saturazione di un'opportunità (da densità di advertiser e velocità d'ingresso di nuovi — proxy, non misura).
- Revenue di terzi (da recensioni/ranking/segnali indiretti — ordine di grandezza, non cifra).
- Fase del ciclo di vita di un'opportunità (classificazione con incertezza).

### C. Non conoscibili [nessun modello li recupera — vietato fingerlo]

- Margini reali e P&L dei concorrenti; se un competitor che spende molto stia guadagnando o bruciando cassa (l'ambiguità centrale del settore: spesa alta ≠ profitto).
- Conversion rate e LTV interni altrui.
- Accordi privati (payout negoziati individualmente, esclusive, sconti media).
- Intenzioni delle piattaforme (cambi di algoritmo/policy prima che avvengano).
- Il controfattuale delle proprie decisioni (cosa avrebbe reso l'opportunità scartata) — mitigabile solo con allocazioni di controllo, mai eliminabile.

**Regola di disciplina:** ogni dato nel sistema porta l'etichetta A/B/C. Un modello che tratta una stima B come un fatto A produce fiducia non guadagnata — è il difetto n.1 dei tool esistenti, e replicarlo azzererebbe la ragione d'essere del progetto.

---

## 9. Metriche costruibili — utili e inutili

Nessuna delle seguenti è "predittiva" fino a prova contraria: sono *candidate*, con il razionale per cui meritano il test.

### Candidate promettenti (con motivazione)

1. **Longevità dei creativi (ad survival).** Un annuncio che resta attivo 60–90 giorni sta quasi certamente pagando per chi lo gestisce: è l'unico segnale pubblico che incorpora il P&L privato di qualcun altro. Razionale forte perché è *rivelazione di preferenza*, non dichiarazione. La più promettente della lista.
2. **Velocità di ingresso di nuovi advertiser su un'opportunità (momentum competitivo).** Misura la parte destra o sinistra del ciclo di vita: utile in entrambe le direzioni (conferma di domanda vs allarme saturazione). Il segno della sua correlazione con l'outcome è esso stesso un'ipotesi interessante.
3. **Churn degli advertiser (tasso di abbandono).** Chi entra e esce in 2 settimane ha testato e perso: un'opportunità con alto turnover e pochi incumbent longevi è una trappola osservabile.
4. **Stabilità/deriva del payout dichiarato nel tempo.** Un network che alza i payout segnala competizione per gli affiliati (domanda di traffico); che li taglia, margine in compressione. Osservabile con precisione, economicamente interpretabile.
5. **Rapporto tra crescita della domanda (trend/social) e crescita dell'offerta (advertiser).** La "greppia vuota": domanda in crescita con competizione piatta è la definizione operativa di opportunità. È la metrica-tesi del progetto: se non funziona lei, l'idea centrale è in dubbio.
6. **Età dell'opportunità alla prima osservazione + posizione nel ciclo di vita stimata contro coorti comparabili.** Contestualizza tutte le altre: gli stessi valori assoluti significano cose opposte a fasi diverse.
7. **Concentrazione dei promotori (pochi grossi vs molti piccoli).** Struttura di mercato dell'opportunità: molti piccoli = accessibile ma affollabile; pochi grossi = barriere (accordi privati probabili, cfr. §8C).

### Probabilmente inutili o dannose (con motivazione)

- **Follower count e metriche di vanità statiche.** Livelli senza derivate, manipolabili, notoriamente scorrelate dalla conversione.
- **EPC/EPM dichiarati dai network presi come verità.** Sono marketing del network (medie su popolazioni selezionate); utilizzabili solo come *segnale della loro variazione*, mai come stima del proprio risultato atteso.
- **Indici compositi non validati ("Opportunity Score 87/100").** Sommare segnali non validati con pesi arbitrari produce pseudo-precisione — è ciò che fanno i competitor consumer, ed è esattamente ciò che il §10 vieta.
- **Sentiment score generici.** Il sentiment sul prodotto non è il sentiment sull'*opportunità di promuoverlo*; segnale debolissimo con costo di raccolta alto.
- **Centinaia di feature ridondanti.** Il pitch dice "centinaia di indicatori al giorno" come se fosse un pregio: con poche etichette è un difetto (cfr. §2.2.5). Meglio 15 segnali con razionale economico che 300 senza.

---

## 10. Opportunity Confidence Score — spiegabile per costruzione

**Posizione del comitato: nel primo anno questo score non deve esistere come numero singolo.** Un punteggio composito prima della validazione è pseudo-scienza con la UI. Ciò che si costruisce subito è la *struttura* che un giorno potrà diventare uno score.

### Architettura a componenti (ognuna leggibile, testabile e scartabile da sola)

1. **Demand (domanda):** evidenza che l'interesse cresce — trend, social, ricerca. Solo dati A/B etichettati.
2. **Competition (pressione competitiva):** densità, momentum d'ingresso, churn, concentrazione dei promotori (§9.2/3/7).
3. **Economics (qualità economica dichiarata):** payout, sua deriva, meccanica dell'offerta (§9.4) — con l'avvertenza che è tutto "dichiarato".
4. **Durability (durabilità):** longevità dei creativi incumbent, età e fase del ciclo di vita (§9.1/6).
5. **Fit (idoneità operativa):** compatibilità con le capacità di CHI decide — canali padroneggiati, capitale, geografie. Non è una proprietà dell'opportunità: per questo un singolo numero "oggettivo" è concettualmente sbagliato.
6. **Data Confidence (meta-componente):** quanta parte del quadro poggia su dati A vs stime B, freschezza, copertura. Due opportunità con lo stesso profilo e Data Confidence diversa NON sono equivalenti — questa componente esiste per impedire al sistema di nascondere la propria ignoranza.

### Regole non negoziabili

- **Ogni componente mostra i suoi input:** dal punteggio si arriva in due passaggi alle Observation grezze che lo generano. Auditabilità totale.
- **Pesi: dichiarati prima, appresi poi.** Fase 1 (anno 1): pesi uniformi o dettati da razionale economico esplicito, dichiarati come non validati — il "punteggio" è di fatto una checklist strutturata. Fase 2: pesi stimati sulle etichette solo quando ce ne sono abbastanza (ordine: centinaia), con metodi che restano leggibili (modelli additivi/lineari con vincoli di monotonicità dichiarati, non ensemble opachi). Se servisse una black box per avere segnale, meglio saperlo e deciderlo — non arrivarci per pigrizia.
- **Output = previsione, non voto.** Non "87/100" ma: "sopra la mediana della coorte comparabile su Durability e Demand; sotto su Competition; probabilità stimata di sopravvivenza a 90 giorni: X% ± Y". Ogni score emesso è una predizione pre-registrata che rientra nell'anello di calibrazione (§7): lo score viene *pagellato* continuamente, e la sua pagella è pubblica dentro il sistema.
- **Lo score può dire "non lo so".** Sotto una soglia di Data Confidence, l'output corretto è l'astensione, non un numero tiepido.

---

## 11. Piano di ricerca — 12 mesi (ricerca, non sviluppo)

**Budget di riferimento: 2–3 persone, strumenti minimi, zero piattaforma.** Ogni trimestre ha un kill criterion esplicito: la ricerca che non può fallire non è ricerca.

### Q1 — Fattibilità dell'osservazione (mesi 1–3)
- **Audit delle fonti:** per ciascuna: cosa è osservabile, a che costo, con che stabilità, con che vincoli legali/ToS. Deliverable: matrice fonti con classificazione A/B/C (§8) e rischio di accesso. *(attacca A4)*
- **Pilota di tracking:** 200–500 opportunità in 3–4 verticali diversi, osservate giornalmente con pipeline volutamente rozze. Obiettivo: scoprire i problemi reali di entity resolution e schema drift, non costruire infrastruttura.
- **Definizione operativa di "morte" e "saturazione" di un'opportunità** — misurabili dall'osservazione, perché saranno le etichette gratuite dell'anello di calibrazione (§7.1).
- **Kill criterion Q1:** se meno di ~50% delle opportunità è osservabile con continuità e risolvibile tra fonti, il registro non è costruibile così com'è → ridisegno del perimetro fonti prima di proseguire.

### Q2 — Studio retrospettivo + inizio previsioni pre-registrate (mesi 4–6)
- **Retrospettiva:** sulle coorti Q1 (e su storico ricostruibile), analisi di sopravvivenza: quali segnali al tempo T distinguono le opportunità vive a T+90 da quelle morte? Con correzione rigorosa per test multipli e holdout intoccato. *(attacca A1 in forma debole)*
- **Prediction journal:** da metà Q2, ogni settimana il team pre-registra previsioni falsificabili su eventi osservabili ("l'offerta X sarà ancora promossa da >N advertiser tra 60 giorni"), sia model-based sia a intuito umano, sigillo temporale, verifica automatica alla scadenza. *(attacca A1 in forma forte + A10, senza spendere capitale)*
- **Misura del lag segnale→saturazione** sulle coorti osservate. *(attacca A2)*
- **Kill criterion Q2:** se nessun segnale supera la retrospettiva corretta per multiple testing, l'anno prosegue ma la tesi va declassata: si continua solo per il valore del journal prospettico.

### Q3 — Etichette a pagamento: allocazioni sperimentali (mesi 7–9)
- **Protocollo di allocazione:** budget di ricerca dedicato (perdita attesa messa a budget come costo esperimento), 15–30 micro-allocazioni: un braccio scelto dal ranking del sistema, un braccio di controllo scelto casualmente tra le ammissibili, esecuzione standardizzata al massimo possibile. *(attacca A6, A7, A10 — e incorpora la lezione Zillow: capitale piccolo, protocollo prima del capitale)*
- Ogni allocazione con previsione economica pre-registrata → primo test di calibrazione sull'anello 2.
- **Test di stabilità tra verticali** dei segnali sopravvissuti a Q2. *(attacca A5)*
- **Kill criterion Q3:** se il braccio sistema non batte il braccio casuale nemmeno in direzione (con N piccolo non si pretende significatività), l'ipotesi A10 è in grave sofferenza.

### Q4 — Calibrazione, regime, verdetto (mesi 10–12)
- **Analisi di calibrazione completa:** Brier/log-score del journal (ormai ~6 mesi di previsioni scadute), sistema vs umano vs base rate.
- **Test A3 (valore dello storico):** le previsioni migliorano usando 9 mesi di storia rispetto a 3? Se no, l'asset "serie temporali lunghe" va ridimensionato nella tesi.
- **Test A9 (regime):** i predittori di Q2 valgono ancora sui dati di Q4?
- **Deliverable finale:** il *Registro delle Ipotesi* — A1–A12 ciascuna con verdetto: confermata / falsificata / indecidibile con questi mezzi — e la raccomandazione strategica: (a) scala prop, (b) consorzio etichette, (c) pivot al layer osservazionale vendibile, (d) stop.

**Cosa NON si fa nei 12 mesi:** knowledge graph, decision engine automatizzato, scoring composito pubblico, prodotto, UI, vendita. Ogni euro speso lì prima dei verdetti è capitale bruciato in infrastruttura per un'ipotesi non testata.

---

## 12. Verdetto del comitato — brutale, come richiesto

### Investiresti $20M oggi?

**No. E non è un no borderline.**

### Perché no

1. **Non è (ancora) una società venture-investibile: è un programma di ricerca.** Zero ricavi previsti per scelta, feedback loop strutturalmente affamato di etichette (A7), ipotesi madre (A1) non testata. Un VC che mette $20M qui sta pagando la ricerca di base di un singolo operatore. Il capitale giusto per i prossimi 12 mesi è $200–500k, e idealmente è capitale proprio o di angel — perché il ritorno della fase 1 è *conoscenza*, non equity value.
2. **Il modello di business è indeciso per progetto, e le opzioni divergono radicalmente.** Prop firm, consorzio dati, SaaS, underwriting: hanno economics, team e rischi incompatibili tra loro. "Decideremo dopo" è accettabile per un founder che rischia il suo tempo; non per $20M di capitale altrui.
3. **Il rischio di fondo non è eliminabile col capitale.** Se i segnali pubblici non anticipano gli outcome (A1 falsa) o l'alpha decade in settimane (A2/A8), nessun investimento lo aggiusta. Il capitale accelera solo ciò che è già dimostrato — e qui non è dimostrato niente. **[FATTO]**
4. **Asimmetria sfavorevole del successo commerciale:** se l'edge esiste ed è vendibile, venderlo lo erode (crowding, §2.2.8); se esiste e non si vende, il business è un prop shop — che i VC tradizionali non finanziano perché non scala come equity tech. La strada stretta che scala davvero (dati/underwriting, §5.4) richiede anni di etichette che oggi non esistono.

### Perché, nonostante tutto, il progetto ha un merito raro

- La domanda è giusta: *migliorare una decisione di allocazione*, non mostrare dashboard. Il 95% dei progetti in quest'area sbaglia proprio qui.
- L'istinto di **non vendere subito e accumulare storico etichettato** è controintuitivo e corretto: è l'unica strada verso un asset non replicabile (§4).
- La richiesta esplicita di distinguere osservabile/stimato/ipotetico indica maturità epistemica superiore alla media dei pitch che questo comitato vede.

Il progetto non è sbagliato. È *prematuro per il venture capital di due o tre gradini*, e la sua versione fondabile dipende da risultati che solo il piano §11 può produrre.

### Milestone per meritare un investimento (in ordine, non negoziabili)

| # | Milestone | Evidenza richiesta |
|---|---|---|
| M1 | **Predittività dimostrata prospetticamente** | ≥6 mesi di previsioni pre-registrate con timestamp; il sistema batte il base rate e la selezione casuale su eventi osservabili (sopravvivenza/saturazione), out-of-sample, con correzione per test multipli |
| M2 | **Superiorità sull'umano o complementarità misurata** | Il ranking del sistema batte (o migliora misurabilmente) la selezione dell'operatore esperto nel torneo di Q3–Q4 (A10) |
| M3 | **Etichette economiche reali** | ≥20–30 allocazioni con protocollo e braccio di controllo; ROI del braccio sistema ≥ braccio casuale con calibrazione documentata |
| M4 | **Sostenibilità dell'accesso ai dati** | Audit legale scritto; ≥2 fonti core con diritto d'accesso stabile (non ToS-fragile); piano B per ogni fonte critica |
| M5 | **Scelta del modello di business** | Una sola strada dichiarata (prop / consorzio / dati / underwriting) con unit economics coerenti e primo segnale esterno (per consorzio/dati: ≥5 operatori terzi che conferiscono outcome o pagano) |

Con M1–M3 il progetto merita un seed serio ($1–2M) per scalare le etichette. Con M1–M5 si può discutere di $20M — che a quel punto finanzierebbero una macchina dimostrata, non un'ipotesi elegante.

### L'avvertimento finale (la regola d'oro del progetto)

Il rischio numero uno non è tecnico, statistico o legale. È **costruire la piattaforma prima dell'evidenza**: pipeline su venti fonti, knowledge graph, decision engine, score — un anno di ingegneria al servizio di un'ipotesi mai messa alla prova. La disciplina che decide il destino di questo progetto sta in una sola frase:

> **Nessuna riga di infrastruttura che non serva a falsificare un'ipotesi numerata.**

Se tra 12 mesi il Registro delle Ipotesi dice che A1 regge, questo comitato vuole rivedere il dossier. Se dice che non regge, il progetto avrà comunque prodotto l'unica cosa che nessun concorrente possiede: la prova di cosa non funziona — comprata al prezzo minimo possibile.
