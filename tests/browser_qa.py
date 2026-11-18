"""Visual QA offline with real SentencePiece tokenization and embedded frontend."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from server import tokenize

html=(root/'static/index.html').read_text()
css=(root/'static/styles.css').read_text()
js=(root/'static/app.js').read_text()
html=html.replace('<link href="/styles.css" rel="stylesheet" />',f'<style>{css}</style>')
mock="""
<script>
window.fetch = async (path,opts) => {
  const data = await window.py_tokenize(JSON.parse(opts.body).text);
  return {ok:true, status:200, json:async()=>data};
};
</script>
"""
html=html.replace('<script src="/app.js" defer></script>',mock)
html=html.replace('</body>',f'<script>{js}</script></body>')

with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
  page=context.new_page()
  page.expose_function('py_tokenize',lambda text: tokenize(text))
  errors=[]
  page.on('pageerror',lambda exc: errors.append(str(exc)))
  page.set_content(html,wait_until='load')
  page.wait_for_function("document.getElementById('metric-tokens').textContent === '10'")
  print('DEFAULT',page.locator('#metric-tokens').inner_text(), 'EXAMPLE',page.locator('#decoded-text').inner_text())
  page.screenshot(path=str(root/'ANTEPRIMA_desktop.png'),full_page=True)
  page.locator('button[data-example="chinese"]').click()
  page.wait_for_function("document.getElementById('metric-unicode').textContent === '15'")
  page.locator('#model-select').select_option('bpe512multi')
  print('CHINESE',page.locator('#metric-tokens').inner_text(),'warning visibile',page.locator('#unknown-warning').is_visible())
  page.screenshot(path=str(root/'ANTEPRIMA_multilingue.png'),full_page=True)
  mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1)
  m=mobile.new_page()
  m.expose_function('py_tokenize',lambda text: tokenize(text))
  m.on('pageerror',lambda exc: errors.append(str(exc)))
  m.set_content(html,wait_until='load')
  m.wait_for_function("document.getElementById('metric-tokens').textContent === '10'")
  widths=m.evaluate('({ scroll: document.documentElement.scrollWidth, inner: window.innerWidth })')
  print('MOBILE WIDTH',widths)
  m.screenshot(path=str(root/'ANTEPRIMA_mobile.png'),full_page=True)
  assert widths['scroll'] <= widths['inner']+1, f'horizontal overflow {widths}'
  assert not errors,errors
  print('BROWSER QA OK')
  browser.close()
