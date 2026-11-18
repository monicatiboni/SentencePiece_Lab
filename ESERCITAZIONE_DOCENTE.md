# Esercitazione in aula (10-15 minuti)

**Titolo:** Le parole diventano token: BPE, Unigram, UTF-8.

**Obiettivo:** capire che il tokenizer suddivide il testo secondo un vocabolario appreso e che token, parole, punti di codice Unicode e byte UTF-8 sono concetti diversi.

**Organizzazione:** il docente invia agli studenti soltanto l'URL pubblico Render. Non servono installazioni, account, codice o chiavi API.

## Attività 1 — un testo tecnico (3 minuti)

1. Scegliere l'esempio **Robotica**.
2. Leggere il conteggio con **BPE 80**; selezionare **BPE 160**.
3. Confrontare i token colorati e gli ID numerici.

**Risultato atteso del corpus incluso:** BPE 80 = **10 token**; BPE 160 = **6 token** per `Il robot lavora nel laboratorio.`. Il vocabolario più grande contiene pezzi più lunghi utili alla frase.

## Attività 2 — lingue diverse (4 minuti)

1. Provare i pulsanti **Italiano**, **English**, **中文**, **日本語**.
2. Osservare se nel tokenizzatore BPE 80 compaiono `<unk>` per alcuni caratteri.
3. Selezionare **BPE 512 multilingue** e verificare se scompaiono.

**Domanda:** perché il tokenizer addestrato su italiano non gestisce necessariamente tutti i caratteri cinesi, mentre un modello multilingue con fallback sui byte li può gestire?

## Attività 3 — UTF-8 e token (3 minuti)

1. Inserire `你好` e osservare il numero di **byte UTF-8**: **6**.
2. Confrontare il numero di **punti di codice Unicode**: **2**.
3. Confrontare il numero di token restituiti dai modelli.

**Conclusione:** byte e token non sono la stessa unità. Il numero di token è specifico del tokenizer.

## Attività 4 — Unigram (facoltativo, 3 minuti)

Confrontare Unigram 64 e BPE 80. Quale parte dell'algoritmo e quale parte della dimensione del vocabolario possono influenzare la segmentazione?

## Osservazioni metodologiche

- Non inferire i prezzi API dal numero di token di questa applicazione: i tokenizer qui sono piccoli modelli **didattici**, non sono i tokenizer di Gemini o GPT.
- I vocabolari BPE 80, BPE 160 e Unigram 64 sono addestrati sullo **stesso corpus italiano**; il BPE 512 usa un corpus diverso e il **byte fallback**.
- Una ricostruzione diversa dal testo può dipendere dalla **normalizzazione** di SentencePiece (per esempio alcuni segni di punteggiatura); viene segnalata nell'interfaccia.
- Alcuni tokenizer possono produrre `<unk>` per simboli mai incontrati: in questo caso il conteggio non è un confronto affidabile tra lingue.
