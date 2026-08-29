#!/usr/bin/env python3
"""Build SEO-friendly ValueRadar product pages, homepage catalogue and sitemap."""
from __future__ import annotations
import html, json, re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'products.json'; OUT=ROOT/'products'; SITEMAP=ROOT/'sitemap.xml'; INDEX=ROOT/'index.html'
VERDICTS={'GOOD_VALUE','GENUINE_DEAL','HIGHLY_RATED','PRICE_DROP','USEFUL_FIND','SKIP'}
SLUG=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
STATIC_URLS=['','about.html','privacy.html','affiliate-disclosure.html','disclaimer.html','terms.html']
START='<!-- PRODUCTS:AUTO:START -->'; END='<!-- PRODUCTS:AUTO:END -->'
SCRIPT_START='<!-- PRODUCT_SEARCH:AUTO:START -->'; SCRIPT_END='<!-- PRODUCT_SEARCH:AUTO:END -->'
VERDICT_ICON={'GOOD_VALUE':'🟢','GENUINE_DEAL':'🔥','HIGHLY_RATED':'⭐','PRICE_DROP':'📉','USEFUL_FIND':'💡','SKIP':'⛔'}

def e(v): return html.escape(str(v or ''), quote=True)
def compact_count(n):
    if not n: return ''
    if n>=100000: return f'{n/100000:.1f}L+'.replace('.0L','L')
    if n>=1000: return f'{n/1000:.1f}K+'.replace('.0K','K')
    return str(n)
def validate(db):
    ids=set(); slugs=set(); errors=[]
    for i,p in enumerate(db.get('products',[]),1):
        tag=p.get('id') or f'product #{i}'
        if not p.get('id') or p['id'] in ids: errors.append(f'{tag}: missing/duplicate id')
        ids.add(p.get('id')); slug=p.get('slug','')
        if not SLUG.fullmatch(slug) or slug in slugs: errors.append(f'{tag}: invalid/duplicate slug')
        slugs.add(slug)
        if p.get('verdict') not in VERDICTS: errors.append(f'{tag}: invalid verdict')
        if p.get('status') not in {'draft','published','archived'}: errors.append(f'{tag}: invalid status')
        if p.get('status')=='published':
            for field in ('name','summary','why_picked','category'):
                if not p.get(field): errors.append(f'{tag}: published product missing {field}')
        for market,allowed in [('amazon','amazon.in'),('flipkart','flipkart.com')]:
            url=p.get('marketplaces',{}).get(market,{}).get('url')
            if url:
                host=urlparse(url).hostname or ''
                if not (host==allowed or host.endswith('.'+allowed)): errors.append(f'{tag}: invalid {market} hostname')
    if errors: raise SystemExit('Product validation failed:\n- '+'\n- '.join(errors))

def market_buttons(p):
    out=[]
    for key,label in [('amazon','Amazon'),('flipkart','Flipkart')]:
        m=p.get('marketplaces',{}).get(key,{})
        if not m.get('url'): continue
        rel='nofollow noopener'+(' sponsored' if m.get('affiliate') else '')
        out.append(f'<a class="market-btn {key}" href="{e(m["url"])}" target="_blank" rel="{rel}" data-marketplace="{label}" data-vr-code="{e(p["id"])}">Check on {label} ↗</a>')
    return ''.join(out) or '<p class="price-note">Marketplace link coming soon.</p>'
def price_signal(s):
    if s.get('price_checked') is None: return None
    label='Tracked reference price' if s.get('price_context')=='third_party_tracker' else 'Marketplace price observed'
    return f'{label} ₹{e(s["price_checked"])}'
def page(p):
    scores=''.join(f'<div class="score-item"><strong>{e(v)}/10</strong><span>{e(k.replace("_"," ").title())}</span></div>' for k,v in p.get('scores',{}).items() if v is not None)
    specs=''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in p.get('specs',{}).items())
    good=''.join(f'<li>{e(x)}</li>' for x in p.get('good_for',[])); watch=''.join(f'<li>{e(x)}</li>' for x in p.get('watch_out',[]))
    s=p.get('signals',{}); signals=[]
    if s.get('rating') is not None: signals.append(f'⭐ {e(s["rating"])}/5')
    if s.get('rating_count'): signals.append(f'{e(s["rating_count"])} ratings')
    ps=price_signal(s)
    if ps: signals.append(ps)
    signal_html=''.join(f'<span>{x}</span>' for x in signals)
    image=p.get('media',{}).get('image'); media=f'<img src="/{e(image.lstrip("/"))}" alt="{e(p.get("media",{}).get("image_alt") or p["name"])}">' if image else '<div class="product-image-placeholder">Product visual</div>'
    verdict=e(p['verdict'].replace('_',' ')); canonical=f'https://valueradar.in/products/{e(p["slug"])}/'; note=e(s.get('price_history_note') or 'Marketplace details can change. Verify before buying.')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p.get('seo',{}).get('title') or p['name'])}</title><meta name="description" content="{e(p.get('seo',{}).get('description') or p['summary'])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/product.css"><script async src="https://www.googletagmanager.com/gtag/js?id=G-BJC6CE45VZ"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-BJC6CE45VZ');</script></head><body><header class="site-header"><div class="container nav-wrap"><a class="brand" href="/"><span class="brand-mark">V</span><span><strong>ValueRadar</strong><small>Find Better. Pay Smarter.</small></span></a></div></header><main class="product-page"><div class="container"><nav class="breadcrumbs"><a href="/">Home</a><span>›</span><span>{e(p['category'])}</span><span>›</span><span>{e(p['id'])}</span></nav><section class="product-hero"><div class="product-media">{media}</div><div class="product-intro"><div class="product-meta"><span class="product-code">{e(p['id'])}</span><span class="product-verdict">{verdict}</span></div><h1>{e(p['name'])}</h1><p class="product-summary">{e(p['summary'])}</p><div class="signal-row">{signal_html}</div><div class="market-buttons">{market_buttons(p)}</div><p class="price-note">{note}</p></div></section><section class="radar-score"><div><span class="eyebrow">VALUERADAR CHECK</span><h2>Our research snapshot</h2></div><div class="score-grid">{scores}</div></section><div class="product-columns"><section class="product-panel"><h2>Why we picked it</h2><p>{e(p['why_picked'])}</p></section><section class="product-panel"><h2>Good for</h2><ul>{good}</ul></section><section class="product-panel watch"><h2>Watch out</h2><ul>{watch}</ul></section><section class="product-panel"><h2>Key details</h2><dl class="spec-list">{specs}</dl></section></div><aside class="research-note"><strong>Research transparency</strong><p>Information checked {e(s.get('checked_at'))}. ValueRadar uses AI-assisted research; marketplace details can change.</p></aside></div></main><footer class="site-footer"><div class="container"><p>© ValueRadar India · <a href="/affiliate-disclosure.html">Affiliate Disclosure</a> · <a href="/privacy.html">Privacy</a> · <a href="/disclaimer.html">Disclaimer</a></p></div></footer><script>document.querySelectorAll('.market-btn').forEach(a=>a.addEventListener('click',()=>{{if(typeof gtag==='function')gtag('event','marketplace_click',{{marketplace:a.dataset.marketplace,vr_code:a.dataset.vrCode,link_url:a.href}})}}));</script></body></html>'''
def home_card(p):
    s=p.get('signals',{}); rating=f'★ {e(s.get("rating"))}/5' if s.get('rating') is not None else 'Research checked'; count=compact_count(s.get('rating_count')); rating += f' · {count} ratings' if count else ''
    price=''; pc=s.get('price_checked')
    if pc is not None: price=f'₹{e(pc)} '+('tracked reference' if s.get('price_context')=='third_party_tracker' else 'observed')
    tokens=' '.join([p['id'],p['name'],p['category'],p['verdict']]).lower().replace('&',' ')
    if pc is not None and pc<500: tokens+=' under500'
    if p['verdict']=='HIGHLY_RATED': tokens+=' highly rated'
    if p['verdict']=='PRICE_DROP': tokens+=' price drop'
    icon=VERDICT_ICON.get(p['verdict'],'•'); label=p['verdict'].replace('_',' ')
    return f'''<article class="preview-card" data-product="{e(tokens)}"><div class="preview-top"><span class="preview-code">{e(p['id'])}</span><span class="preview-status">{icon} {e(label)}</span></div><div class="preview-body"><div class="preview-image">{e(p['id'])}<br>ValueRadar Find</div><div><span class="eyebrow">{e(p['category'].upper())}</span><h3>{e(p['name'])}</h3><p>{e(p['summary'])}</p><div class="preview-metrics"><span><b>★</b> {rating}</span>{f'<span><b>₹</b> {price}</span>' if price else ''}</div><a class="primary-cta" href="/products/{e(p['slug'])}/">View ValueRadar check →</a></div></div></article>'''
def write_home(products):
    published=[p for p in products if p.get('status')=='published']
    text=INDEX.read_text(encoding='utf-8')
    cards='\n'.join(home_card(p) for p in published)
    if START in text and END in text:
        text=text.split(START)[0]+START+'\n'+cards+'\n'+END+text.split(END,1)[1]
    else:
        old=re.search(r'(<div id="productsContainer" class="product-grid">).*?(</div></div></section>\n<section id="method")',text,re.S)
        if not old: raise SystemExit('Homepage productsContainer not found')
        text=text[:old.start()]+old.group(1)+'\n'+START+'\n'+cards+'\n'+END+'\n'+old.group(2)+text[old.end():]
    data=[[p['id'].lower(),f'/products/{p["slug"]}/',' '.join([p['id'],p['name'],p['category']]).lower()] for p in published]
    script=f'''<script>{SCRIPT_START}\nconst products={json.dumps(data,ensure_ascii=False)};\n{SCRIPT_END}const form=document.getElementById('searchForm'),input=document.getElementById('productSearch'),msg=document.getElementById('searchMessage'),cards=[...document.querySelectorAll('.preview-card')];form.addEventListener('submit',e=>{{e.preventDefault();const q=input.value.trim().toLowerCase();if(q&&typeof gtag==='function')gtag('event','site_search',{{search_term:q}});const hit=products.find(p=>p[2].includes(q)&&q.length>1);if(hit){{location.href=hit[1];return}}msg.textContent=q?`No published match for “${{input.value.trim()}}” yet. Try VR001–VR010.`:'Enter a VR code or product name to search.';}});document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{{const f=b.dataset.filter;cards.forEach(c=>{{const d=c.dataset.product;const show=f==='today'||(f==='home'&&d.includes('home'))||(f==='gadgets'&&(d.includes('utility')||d.includes('personal care')))||(f==='under500'&&d.includes('under500'))||(f==='rated'&&d.includes('highly rated'))||(f==='drops'&&d.includes('price drop'));c.style.display=show?'':'none'}});document.getElementById('finds').scrollIntoView({{behavior:'smooth'}});if(typeof gtag==='function')gtag('event','category_interest',{{category_name:b.querySelector('strong').textContent}});}}));document.getElementById('year').textContent=new Date().getFullYear();</script>'''
    text=re.sub(r'<script>const products=.*?</script></body></html>',script+'</body></html>',text,flags=re.S)
    text=text.replace('Four researched products with clear verdicts and transparent price signals.',f'{len(published)} researched products with clear verdicts and transparent price signals.')
    INDEX.write_text(text,encoding='utf-8')
def write_sitemap(products):
    urls=[f'https://valueradar.in/{x}' for x in STATIC_URLS]+[f'https://valueradar.in/products/{p["slug"]}/' for p in products if p.get('status')=='published']
    body='\n'.join(f'  <url><loc>{e(u)}</loc></url>' for u in urls); SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+body+'\n</urlset>\n',encoding='utf-8')
def main():
    db=json.loads(DB.read_text(encoding='utf-8')); validate(db); OUT.mkdir(exist_ok=True); built=[]
    for p in db.get('products',[]):
        if p.get('status')!='published': continue
        d=OUT/p['slug']; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(page(p),encoding='utf-8'); built.append(p['slug'])
    write_home(db.get('products',[])); write_sitemap(db.get('products',[])); print(f'Built {len(built)} product page(s), homepage catalogue and sitemap')
if __name__=='__main__': main()
