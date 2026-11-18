"""Test deterministici per modelli e server HTTP, eseguibili con unittest."""
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from server import tokenize, MODELS


class TokenizerTests(unittest.TestCase):
    def test_models(self):
        self.assertEqual(len(MODELS), 4)
        self.assertEqual({m['key'] for m in MODELS}, {'bpe80','bpe160','unigram64','bpe512multi'})
    def test_italian_example(self):
        out=tokenize('Il robot lavora nel laboratorio.')
        m={x['key']:x for x in out['models']}
        self.assertEqual(m['bpe80']['count'],10)
        self.assertEqual(m['bpe160']['count'],6)
        self.assertTrue(m['bpe80']['same_as_input'])
        self.assertTrue(m['bpe160']['same_as_input'])
    def test_utf8(self):
        out=tokenize('你好')
        self.assertEqual(out['input']['utf8_bytes'],6)
        self.assertEqual(out['input']['unicode_codepoints'],2)
        multi=next(m for m in out['models'] if m['key']=='bpe512multi')
        self.assertEqual(multi['unknown_count'],0)
        self.assertTrue(multi['same_as_input'])
    def test_emoji_fallback(self):
        out=tokenize('Robot 🤖')
        multi=next(m for m in out['models'] if m['key']=='bpe512multi')
        self.assertEqual(multi['unknown_count'],0)
        self.assertTrue(multi['same_as_input'])
    def test_ids_are_real(self):
        out=tokenize('Il robot lavora nel laboratorio.')
        for m in out['models']:
            self.assertEqual(m['count'],len(m['tokens']))
            self.assertTrue(all(isinstance(t['id'],int) for t in m['tokens']))
            self.assertEqual(len(m['tokens']),len([t['piece'] for t in m['tokens']]))


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port='18376'
        env=dict(os.environ,PORT=cls.port)
        cls.proc = subprocess.Popen([sys.executable, str(BASE/'server.py')], cwd=BASE,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,env=env)
        cls.origin=f'http://127.0.0.1:{cls.port}'
        for _ in range(40):
            try:
                with urlopen(cls.origin+'/api/health',timeout=1) as r:
                    if r.status==200:return
            except Exception:
                time.sleep(.1)
        raise RuntimeError('server did not start')
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:cls.proc.kill()
    def post(self,text):
        body=json.dumps({'text':text}, ensure_ascii=False).encode('utf-8')
        req=Request(self.origin+'/api/tokenize',body,{'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=4) as r:
            return r.status,json.load(r)
    def test_health(self):
        with urlopen(self.origin+'/api/health') as r:
            self.assertEqual(r.status,200)
            self.assertEqual(json.load(r)['models'],4)
    def test_page(self):
        with urlopen(self.origin+'/') as r:
            self.assertIn(b'SentencePiece Lab',r.read())
            self.assertIn('no-store',r.headers.get('Cache-Control'))
    def test_resources(self):
        for path in ['/app.js','/styles.css','/api/models']:
            with urlopen(self.origin+path) as r:self.assertEqual(r.status,200)
    def test_post(self):
        status,data=self.post('Il robot lavora nel laboratorio.')
        self.assertEqual(status,200)
        self.assertEqual(data['models'][0]['count'],10)
    def test_unicode_post(self):
        status,data=self.post('你好 🤖')
        self.assertEqual(status,200)
        self.assertEqual(data['models'][-1]['unknown_count'],0)
    def test_empty_text_rejected(self):
        with self.assertRaises(HTTPError) as e:self.post(' ')
        self.assertEqual(e.exception.code,400)
    def test_long_rejected(self):
        with self.assertRaises(HTTPError) as e:self.post('a'*1201)
        self.assertEqual(e.exception.code,413)
    def test_no_source_exposure(self):
        for path in ['/server.py','/models/bpe80.model','/../server.py']:
            with self.assertRaises(HTTPError) as e:urlopen(self.origin+path)
            self.assertEqual(e.exception.code,404)

if __name__=='__main__':unittest.main(verbosity=2)
