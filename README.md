# SentencePiece Lab 2.0 — versione a schede

Questa versione dell'applicazione organizza il laboratorio in **quattro schede**: Scrivi e analizza, Token e ID, Confronta, Comprendi. Per aggiornare la versione già online su Render, vedi `AGGIORNAMENTO_VERSIONE_2.md`.

# SentencePiece Lab — Applicazione web per Render

**Laboratorio universitario di tokenizzazione: BPE, Unigram e byte UTF-8.**

Questa applicazione contiene **tokenizer SentencePiece reali** e un'interfaccia HTML moderna. Gli studenti **non devono installare software, vedere codice, creare account o inserire chiavi API**. Basta fornire il link pubblico di Render.

## Cosa possono fare gli studenti

- Scrivere qualsiasi frase, anche in italiano, inglese, cinese o giapponese.
- Vedere la segmentazione in token e l'ID numerico di ogni token.
- Confrontare **BPE (80 token), BPE (160), Unigram (64) e BPE multilingue (512)**.
- Contare i byte UTF-8 e i punti di codice Unicode; osservare che non coincidono necessariamente con i token.
- Vedere la ricostruzione del testo e l'eventuale presenza di `<unk>`.

**Nota:** il corpus è piccolo e dimostrativo. I numeri non sono i token di Gemini, GPT o altri LLM commerciali e non corrispondono a costi delle API.

## Pubblicazione con GitHub + Render (senza installazioni sui PC)

1. Apri https://github.com/new e crea un repository, ad esempio `sentencepiece-lab` (può essere pubblico).
2. Estrai lo ZIP e **carica tutti i file e la cartella `models` e `static`** nella radice del repository. Il file `server.py` deve trovarsi allo stesso livello di `requirements.txt`, `render.yaml`, `.python-version`.
3. Premi **Commit changes**.
4. Apri https://dashboard.render.com/ e scegli **New → Web Service**; collega il nuovo repository GitHub.
5. Inserisci:

   | Campo Render | Valore |
   |---|---|
   | Language | **Python 3** (NON Node) |
   | Branch | `main` |
   | Root Directory | lasciare vuoto |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `python server.py` |
   | Instance Type | **Free** |
   | Environment variables | **nessuna** |
   | Health Check Path (se richiesto) | `/api/health` |

6. Premi **Deploy Web Service** e attendi che risulti **Live**.
7. Apri l'URL assegnato da Render (`https://<nome>.onrender.com`) e distribuisci **solo questo link** agli studenti.

In alternativa: **New → Blueprint**, seleziona il repository. Il file `render.yaml` contiene già le impostazioni di deployment, compreso il piano Free. Prima di confermare, verifica che il piano sia Free.

**Attenzione:** il piano Free di Render può sospendere l'istanza dopo un periodo di inattività, causando un ritardo al primo accesso. Per una lezione, apri il sito prima dell'inizio.

## Prova rapida

1. Avvia una tokenizzazione con `Il robot lavora nel laboratorio.`.
2. Confronta il modello BPE 80 con BPE 160. Sul corpus incluso ottieni normalmente **10 token contro 6**.
3. Cambia testo in `你好，欢迎来到人工智能实验室。`. Alcuni modelli italiani restituiscono `<unk>` perché non hanno appreso i caratteri cinesi.
4. Seleziona **BPE multilingue 512**: il modello è stato addestrato anche su testo cinese e ha un meccanismo di **byte fallback**.
5. Distingui il numero di byte UTF-8 dal numero di token.

## Esecuzione locale opzionale (solo docente)

Se sul proprio computer sono disponibili Python e le dipendenze:

```bash
pip install -r requirements.txt
python server.py
```

Apri `http://localhost:10000`. Su Render, la porta è letta automaticamente dalla variabile `PORT`.

I modelli `.model` sono **già addestrati e inclusi**: non serve eseguire `train_models.py`. Il file `train_models.py` documenta il metodo utilizzato e permette a un docente di riprodurre l'addestramento.

## Architettura e privacy

- Backend minimale in Python con `ThreadingHTTPServer` e libreria `sentencepiece`.
- Frontend HTML/CSS/JavaScript, senza CDN o framework esterni.
- I modelli vengono caricati una sola volta all'avvio; il server gestisce più richieste contemporanee.
- Le frasi sono elaborate solo in memoria; non sono memorizzate in file o database e il programma non registra i testi nei log.
- Non usa Google AI Studio, servizi Gemini, API key o chiamate a LLM.
- Limite di 1.200 punti di codice Unicode per richiesta per prevenire carichi eccessivi.
- Collegamento HTTPS gestito da Render.

Per grandi classi consigliamo di testare la risposta del piano Free prima della lezione, perché potenza e quote sono limitate.

## Contenuti dello ZIP

- `static/index.html`, `static/styles.css`, `static/app.js` — interfaccia.
- `server.py` — server HTTP e tokenizzazione.
- `models/*.model` — quattro tokenizer pre-addestrati.
- `models/*.vocab` e corpus — materiale didattico, non obbligatorio per l'esecuzione.
- `train_models.py` — script riproducibile di addestramento (facoltativo).
- `render.yaml`, `.python-version`, `requirements.txt` — configurazione Render.
- `tests/test_lab.py` — test automatici.

## Riferimenti

- SentencePiece: https://github.com/google/sentencepiece
- Documentazione SentencePiece: https://google.github.io/sentencepiece/
- Render: https://render.com/docs/deploys
