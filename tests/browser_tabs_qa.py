from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from server import tokenize
html = (root/'static/index.html').read_text()
css = (root/'static/styles.css').read_text()
js = (root/'static/app.js').read_text()
html=html.replace('<link href="/styles.css" rel="stylesheet" />','<style>'+css+'</style>')
html=html.replace('<script src="/app.js" defer></script>', '''<script>
window.fetch = async (url,opts) => ({ok:true,status:200,json:async()=>window.py_tokenize(JSON.parse(opts.body).text)});
</script>''')
html=html.replace('</body>',f'<script>{js}</script></body>')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(1440,900),(1366,768),(1280,720),(390,844)]:
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  page.expose_function('py_tokenize',lambda text:tokenize(text))
  errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.set_content(html,wait_until='load')
  page.wait_for_function("document.getElementById('metric-tokens').textContent === '10'")
  sizes=page.evaluate('''() => ({vw:innerWidth,vh:innerHeight, bodyHeight:document.body.scrollHeight, htmlHeight:document.documentElement.scrollHeight, width:document.documentElement.scrollWidth, main:document.querySelector('.lab-panels').clientHeight})''')
  assert sizes['width']<=width+2,('horizontal',sizes)
  for tab in ['write','tokens','compare','learn']:
   page.locator('[data-tab="'+tab+'"]').click()
   assert page.locator('[data-panel="'+tab+'"]').is_visible(),tab
   metrics=page.evaluate('''name => {
      const panel=document.querySelector(`[data-panel="${name}"]`);
      const inner=panel.querySelector('.write-layout, .results, .comparison, .learning');
      return {panelClient:panel.clientHeight,panelScroll:panel.scrollHeight, innerClient:inner?.clientHeight, innerScroll:inner?.scrollHeight};
   }''',tab)
   print(f'{width}x{height} {tab}:',metrics)
   if width>=1280 and height>=720:
    assert metrics['panelScroll']<=metrics['panelClient']+3, (width,height,tab,metrics)
   if tab=='write' and width==1440:page.screenshot(path=str(root/'ANTEPRIMA_SCHEDA_1.png'))
   if tab=='tokens' and width==1440:page.screenshot(path=str(root/'ANTEPRIMA_SCHEDA_2.png'))
   if tab=='compare' and width==1440:page.screenshot(path=str(root/'ANTEPRIMA_SCHEDA_3.png'))
   if tab=='learn' and width==1440:page.screenshot(path=str(root/'ANTEPRIMA_SCHEDA_4.png'))
  page.locator('[data-tab="write"]').click()
  page.locator('#analyze-btn').click()
  page.wait_for_function("document.getElementById('tab-tokens').getAttribute('aria-selected')==='true'")
  page.locator('[data-goto="compare"]').first.click()
  assert page.locator('[data-panel="compare"]').is_visible()
  page.locator('[data-tab="write"]').click()
  page.locator('[data-example="chinese"]').click()
  page.wait_for_function("document.getElementById('metric-unicode').textContent==='15'")
  assert page.locator('[data-panel="tokens"]').is_visible()
  assert not errors,errors
  print(f'{width}x{height} QA PASS; viewport',sizes)
  page.close()
 browser.close()
