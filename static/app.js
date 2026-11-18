(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const textEl = $('input-text');
  const selectEl = $('model-select');
  const examples = {
    robot: 'Il robot lavora nel laboratorio.',
    industrial: 'Il sensore misura la temperatura del cilindro pneumatico.',
    italian: 'Ciao! Come stai oggi?',
    english: 'Hello! How are you today?',
    chinese: '你好，欢迎来到人工智能实验室。',
    japanese: 'こんにちは、世界。ロボットの研究室です。',
  };
  let latest = null;
  let inflight = false;
  let requestIndex = 0;
  const tabs = Array.from(document.querySelectorAll('[role="tab"][data-tab]'));
  const panels = Array.from(document.querySelectorAll('[role="tabpanel"][data-panel]'));
  function activateTab(name, focus = false) {
    const target = tabs.find(tab => tab.dataset.tab === name);
    if (!target) return;
    tabs.forEach(tab => {
      const active = tab === target;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    panels.forEach(panel => {
      const active = panel.dataset.panel === name;
      panel.hidden = !active;
      panel.classList.toggle('active', active);
      if (active) panel.scrollTop = 0;
    });
    if (focus) target.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab.dataset.tab));
    tab.addEventListener('keydown', event => {
      let offset = 0;
      if (event.key === 'ArrowRight') offset = 1;
      else if (event.key === 'ArrowLeft') offset = -1;
      else if (event.key === 'Home') offset = -index;
      else if (event.key === 'End') offset = tabs.length - 1 - index;
      else return;
      event.preventDefault();
      activateTab(tabs[(index + offset + tabs.length) % tabs.length].dataset.tab, true);
    });
  });
  document.querySelectorAll('[data-goto]').forEach(button => {
    button.addEventListener('click', () => activateTab(button.dataset.goto, true));
  });
  const charCount = () => [...textEl.value].length;

  function updateCount() {
    $('character-count').textContent = `${charCount()} / 1200`;
  }
  function setStatus(text, isError = false) {
    const el = $('status');
    el.textContent = text;
    el.classList.toggle('failed', isError);
    if (!isError) {
      const dot = document.createElement('span');
      dot.className = 'status-dot';
      el.prepend(dot);
    }
  }
  function el(tag, classes, text) {
    const node = document.createElement(tag);
    if (classes) node.className = classes;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function markPreset(key) {
    document.querySelectorAll('[data-example]').forEach(button => {
      button.classList.toggle('active', button.dataset.example === key);
    });
  }
  function showError(error) {
    setStatus('Errore', true);
    const board = $('token-board');
    board.replaceChildren(el('span','placeholder',error));
    $('compare-grid').replaceChildren(el('span','placeholder', 'Non è stato possibile completare il confronto.'));
    $('metric-tokens').textContent = '—';
    $('metric-bytes').textContent = '—';
    $('metric-unicode').textContent = '—';
    $('decoded-text').textContent = '—';
    activateTab('tokens');
    $('match-badge').textContent = '—';
    $('unknown-warning').classList.add('hidden');
  }
  function renderSelected() {
    if (!latest) return;
    const selected = latest.models.find(model => model.key === selectEl.value) || latest.models[0];
    if (!selected) return;
    $('model-label').textContent = selected.label;
    $('metric-tokens').textContent = selected.count;
    $('metric-bytes').textContent = latest.input.utf8_bytes;
    $('metric-unicode').textContent = latest.input.unicode_codepoints;
    $('compare-text-snippet').textContent = `Testo: ${textEl.value.slice(0,100)}${textEl.value.length > 100 ? '…' : ''}`;
    const board = $('token-board');
    board.replaceChildren();
    selected.tokens.forEach((token, idx) => {
      const chip = el('div', `token-chip${token.unknown ? ' unknown' : ''}`);
      chip.title = `Token ${idx + 1}: ${token.piece} · ID ${token.id}`;
      chip.append(el('div', 'token-piece', token.piece));
      chip.append(el('div', 'token-id', `ID ${token.id}`));
      board.append(chip);
    });
    $('decoded-text').textContent = selected.decoded || '—';
    const match = $('match-badge');
    match.classList.toggle('warning-badge', !selected.same_as_input);
    match.textContent = selected.same_as_input ? '✓ Testo ricostruito' : '≠ Ricostruzione diversa';
    const warning = $('unknown-warning');
    if (selected.unknown_count) {
      warning.textContent = `${selected.unknown_count} token sconosciuto/i (<unk>) con questo vocabolario: la ricostruzione potrebbe perdere informazioni. Prova BPE multilingue per analizzare il testo.`;
      warning.classList.remove('hidden');
    } else if (!selected.same_as_input) {
      warning.textContent = 'SentencePiece può normalizzare alcuni caratteri o spazi. Per questo la ricostruzione non è sempre identica al testo inserito.';
      warning.classList.remove('hidden');
    } else {
      warning.classList.add('hidden');
    }
    renderComparisons(selected.key);
  }
  function renderComparisons(key) {
    const parent = $('compare-grid');
    parent.replaceChildren();
    const maxCount = Math.max(1, ...latest.models.map(model => model.count));
    latest.models.forEach(model => {
      const card = el('article', 'compare-card' + (model.key === key ? ' selected' : '') + (model.unknown_count ? ' unknown-card' : ''));
      card.append(el('div', 'compare-name', model.label));
      card.append(el('div', 'compare-sub', `${model.algorithm} · corpus: ${model.corpus}`));
      const n = el('div', 'compare-big', model.count);
      n.append(el('span', 'compare-small', 'token'));
      card.append(n);
      const bar = document.createElement('progress');
      bar.max = maxCount;
      bar.value = model.count;
      bar.setAttribute('aria-label', `Token: ${model.count}`);
      card.append(bar);
      const note = model.unknown_count
        ? `${model.unknown_count} token sconosciuto/i: confronto da interpretare con cautela.`
        : (model.same_as_input ? 'Testo ricostruito correttamente.' : 'Il testo ricostruito presenta differenze.');
      card.append(el('div', 'compare-summary', note));
      parent.append(card);
    });
  }
  async function analyze(switchAfter = true) {
    if (inflight) return;
    const text = textEl.value;
    if (!text.trim()) { showError('Inserisci un testo da tokenizzare.'); return; }
    if (charCount() > 1200) { showError('Il testo supera il limite massimo di 1200 caratteri Unicode.'); return; }
    inflight = true;
    $('analyze-btn').disabled = true;
    setStatus('Analisi in corso');
    const current = ++requestIndex;
    try {
      const response = await fetch('/api/tokenize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({text}),
      });
      let payload = {};
      try { payload = await response.json(); } catch { /* gracefully handle unexpected response */ }
      if (!response.ok) throw new Error(payload.error || `Errore HTTP ${response.status}`);
      if (current !== requestIndex) return;
      latest = payload;
      renderSelected();
      setStatus('Analisi completata');
      if (switchAfter) activateTab('tokens');
    } catch (error) {
      latest = null;
      showError(error.message || 'Connessione al server non riuscita. Riprova.');
    } finally {
      inflight = false;
      $('analyze-btn').disabled = false;
    }
  }
  document.querySelectorAll('[data-example]').forEach(button => {
    button.addEventListener('click', () => {
      const name = button.dataset.example;
      textEl.value = examples[name] || '';
      markPreset(name);
      updateCount();
      analyze(true);
    });
  });
  $('analyze-btn').addEventListener('click', () => analyze(true));
  selectEl.addEventListener('change', renderSelected);
  textEl.addEventListener('input', () => {
    markPreset('');
    updateCount();
  });
  textEl.addEventListener('keydown', event => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault(); analyze(true);
    }
  });
  updateCount();
  analyze(false);
})();
