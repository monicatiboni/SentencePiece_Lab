"""SentencePiece Lab - web server con sola libreria standard Python + SentencePiece.
Nessuna API esterna, chiave, database o logging dei testi inseriti.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import sentencepiece as spm

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / 'models'
STATIC_DIR = ROOT / 'static'
MAX_CHARS = 1200
MAX_BODY_BYTES = 12000
MODELS = [
    dict(key='bpe80', label='BPE · 80', algorithm='BPE', size=80, corpus='Italiano', description='Vocabolario piccolo: piu segmenti per la stessa frase.'),
    dict(key='bpe160', label='BPE · 160', algorithm='BPE', size=160, corpus='Italiano', description='Vocabolario piu ampio, stesso corpus di addestramento.'),
    dict(key='unigram64', label='Unigram · 64', algorithm='Unigram', size=64, corpus='Italiano', description='Algoritmo diverso, addestrato sullo stesso corpus.'),
    dict(key='bpe512multi', label='BPE · 512 multilingue', algorithm='BPE (byte fallback)', size=512, corpus='Italiano, inglese, cinese, giapponese', description='Vocabolario multilingue, con fallback sui byte.'),
]
TOKENIZERS = {}
for model in MODELS:
    path = MODEL_DIR / (model['key'] + '.model')
    if not path.is_file():
        raise RuntimeError(f'Modello mancante: {path}')
    tokenizer = spm.SentencePieceProcessor(model_file=str(path))
    model['size'] = tokenizer.get_piece_size()
    TOKENIZERS[model['key']] = tokenizer


def tokenize(text: str):
    """Esegue sul server tutti i tokenizer, senza dati persistenti."""
    output = []
    for meta in MODELS:
        tokenizer = TOKENIZERS[meta['key']]
        ids = tokenizer.encode(text, out_type=int)
        pieces = [tokenizer.id_to_piece(v) for v in ids]
        decoded = tokenizer.decode(ids)
        unknown = sum(1 for v in ids if v == tokenizer.unk_id())
        output.append({
            **meta,
            'count': len(ids),
            'unknown_count': unknown,
            'tokens': [{'id': ident, 'piece': piece, 'unknown': ident == tokenizer.unk_id()}
                       for ident, piece in zip(ids, pieces)],
            'decoded': decoded,
            'same_as_input': decoded == text,
        })
    return {
        'input': {
            'text': text,
            'unicode_codepoints': len(text),
            'utf8_bytes': len(text.encode('utf-8')),
        },
        'models': output,
        'note': 'I modelli sono didattici, addestrati su piccoli corpus; non rappresentano i tokenizer ufficiali degli LLM commerciali.'
    }


class Handler(BaseHTTPRequestHandler):
    server_version = 'SentencePieceLab/1.0'
    sys_version = ''

    def log_message(self, format, *args):
        # Evita log di URL o contenuti sensibili. Il progetto non salva testi.
        return

    def _common_headers(self, mime: str):
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
                         "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")

    def _json(self, status: int, content: dict):
        data = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self._common_headers('application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _static(self, filename: str, mime: str):
        content = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self._common_headers(mime)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            self._static('index.html', 'text/html; charset=utf-8')
        elif path == '/styles.css':
            self._static('styles.css', 'text/css; charset=utf-8')
        elif path == '/app.js':
            self._static('app.js', 'text/javascript; charset=utf-8')
        elif path == '/api/health':
            self._json(200, {'status':'ok', 'models':len(TOKENIZERS)})
        elif path == '/api/models':
            self._json(200, {'models': MODELS, 'max_chars':MAX_CHARS})
        else:
            self._json(404, {'error':'Risorsa non trovata.'})

    def do_POST(self):
        if urlparse(self.path).path != '/api/tokenize':
            self._json(404, {'error':'Risorsa non trovata.'})
            return
        if not self.headers.get('Content-Type','').lower().startswith('application/json'):
            self._json(415, {'error':'Inviare dati JSON.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = 0
        if not 0 < length <= MAX_BODY_BYTES:
            self._json(413, {'error':'Richiesta troppo grande o vuota.'})
            return
        try:
            data = json.loads(self.rfile.read(length))
        except (UnicodeError, json.JSONDecodeError):
            self._json(400, {'error':'Formato JSON non valido.'})
            return
        if not isinstance(data, dict) or not isinstance(data.get('text'), str):
            self._json(400, {'error':'Inserire un testo valido.'})
            return
        text = data['text']
        if not text.strip():
            self._json(400, {'error':'Inserire almeno una parola.'})
            return
        if len(text) > MAX_CHARS:
            self._json(413, {'error':f'Massimo {MAX_CHARS} punti di codice Unicode.'})
            return
        try:
            result = tokenize(text)
            self._json(200, result)
        except Exception:
            self._json(500, {'error':'Errore nella tokenizzazione.'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT','10000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'SentencePiece Lab disponibile sulla porta {port}', flush=True)
    server.serve_forever()
