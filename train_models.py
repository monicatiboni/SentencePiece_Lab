"""Utility SOLO per il docente. I modelli addestrati sono gia inclusi nello ZIP.
Riproduce l'esempio universitario originale dei vocabolari 80/160.
"""
from pathlib import Path
import sentencepiece as spm

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / 'models'
MODELS.mkdir(exist_ok=True)
phrases = [
    'Il robot lavora nel laboratorio universitario.',
    'Il robot collabora con lo studente.',
    'Il laboratorio usa un robot collaborativo.',
    'Lo studente programma il robot.',
    'Il robot esegue un movimento controllato.',
    'Il sensore misura la posizione del robot.',
    'La programmazione del robot e importante.',
    'Il robot lavora in sicurezza con le persone.',
]
corpus = MODELS / 'corpus_italiano.txt'
corpus.write_text('\n'.join(phrases * 24) + '\n', encoding='utf-8')
for method, size, prefix in [
    ('bpe', 80, 'bpe80'), ('bpe', 160, 'bpe160'), ('unigram', 64, 'unigram64')
]:
    spm.SentencePieceTrainer.train(
        input=str(corpus), model_prefix=str(MODELS / prefix),
        model_type=method, vocab_size=size,
        character_coverage=1.0, hard_vocab_limit=False,
        minloglevel=2,
    )

multilingual = [
  'Il robot lavora nel laboratorio universitario.', 'Il robot collabora con lo studente.',
  'Il sensore misura la temperatura del cilindro pneumatico.',
  'Un sistema di controllo regola la velocità del motore.',
  'Il cilindro pneumatico sviluppa una forza nella corsa.',
  'Calcoliamo la pressione la portata e la coppia del motore.',
  'Buongiorno, grazie e arrivederci! Ciao amici.',
  'Intelligenza artificiale: modelli linguistici e tokenizzazione.',
  'The robot works in the university laboratory.',
  'The robot collaborates with the student in the laboratory.',
  'The sensor measures the position of the robot arm.',
  'Hello, good morning, thank you, and goodbye!',
  'Artificial intelligence and language models can process texts.',
  'We compare tokens, bytes and characters in different languages.',
  '你好，世界！机器人的实验室。',
  '你好，欢迎来到人工智能实验室。',
  '机器人正在实验室工作。',
  '我们使用不同语言比较文本和标记。',
  '人工智能模型可以分析文本信息。',
  'こんにちは、世界。ロボットの研究室です。',
  'ロボットは大学の研究室で動作します。',
  '人工知能のモデルで文章を分析します。',
  '異なる言語でトークンの数を比較します。',
]
multicorpus = MODELS / 'corpus_multilingue.txt'
multicorpus.write_text('\n'.join(multilingual * 24) + '\n', encoding='utf-8')
spm.SentencePieceTrainer.train(
  input=str(multicorpus), model_prefix=str(MODELS / 'bpe512multi'),
  model_type='bpe', vocab_size=512, character_coverage=1.0,
  byte_fallback=True, hard_vocab_limit=False, minloglevel=2,
)
print('Modelli creati:')
for p in sorted(MODELS.glob('*.model')):
    s = spm.SentencePieceProcessor(model_file=str(p))
    print(p.name, s.get_piece_size(), p.stat().st_size)
