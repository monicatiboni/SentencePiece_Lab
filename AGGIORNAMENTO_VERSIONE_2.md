# SentencePiece Lab 2.0 — Schede per schermo intero

La versione 2.0 dispone di quattro schede indipendenti progettate per stare interamente nello schermo di un PC in aula, senza scorrere un'unica lunga pagina:

1. **Scrivi e analizza:** inserimento del testo, esempi rapidi e scelta del tokenizer; guida essenziale al flusso di lavoro.
2. **Token e ID:** visualizzazione dei token reali di SentencePiece, identificativi numerici, byte UTF-8, punti di codice Unicode, ricostruzione del testo e gestione di `<unk>`.
3. **Confronta:** confronto simultaneo di BPE 80, BPE 160, Unigram 64 e BPE multilingue 512.
4. **Comprendi:** domande guidate e sintesi delle differenze fra BPE, Unigram e UTF-8.

Quando si preme **Analizza la tokenizzazione**, si apre automaticamente la scheda dei risultati. Il testo e i risultati rimangono disponibili passando da una scheda all'altra. Si possono cambiare le schede anche con le frecce della tastiera quando è selezionata la barra di navigazione.

## Aggiornamento del repository GitHub già pubblicato su Render

Per aggiornare la precedente SentencePiece Lab senza creare una nuova applicazione, **sostituisci solo** questi tre file, mantenendoli nella cartella `static` del repository GitHub:

- `static/index.html`
- `static/styles.css`
- `static/app.js`

Premi **Commit changes**. Render normalmente rileva il commit e pubblica la nuova versione in automatico. Al termine, ricarica il sito con `Ctrl+F5` per evitare la cache del browser. I quattro modelli SentencePiece già presenti sul server e il motore Python non devono essere sostituiti.

## Compatibilità e test

- Test Python: 13/13 superati senza modificare gli algoritmi di tokenizzazione.
- Controlli frontend: quattro schede navigabili, passaggio automatico all'analisi, esempi multilingue e assenza di errori JavaScript.
- Desktop: viewport 1440×900, 1366×768 e 1280×720 verificati senza scorrimento della pagina o dei pannelli con i testi di prova.
- Smartphone: verifica su viewport 390×844; per alcuni contenuti è previsto uno scorrimento interno alla scheda.
- Testi eccezionalmente lunghi possono rendere necessario scorrere **dentro il riquadro dei token**; la pagina principale rimane ferma.

L'applicazione non richiede chiavi API e non effettua chiamate a LLM. Le quattro tokenizzazioni sono calcolate dai modelli inclusi nel progetto.
