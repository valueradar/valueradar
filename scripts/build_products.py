#!/usr/bin/env python3
"""Build SEO-friendly static ValueRadar product pages from products.json."""
from __future__ import annotations
import html, json, re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'products.json'
OUT=ROOT/'products'
VERDICTS={'GOOD_VALUE','GENUINE_DEAL','HIGHLY_RATED','PRICE_DROP','USEFUL_FIND','SKIP'}
SLUG=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def e(v): return html.escape(str(v or ''), quote=True)
def validate(db):
    ids=set(); slugs=set(); errors=[]
    for i,p in enumerate(db.get('products',[]),1):
        tag=p.get('id') or f'product #{i}'
        if not p.get('id') or p['id'] in ids: errors.append(f'{tag}: missing/duplicate id')
        ids.add(p.get('id'))
        slug=p.get('slug','')
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

def page(p):
    scores=''.join(f'<div class="score-item"><strong>{e(v)}/10</strong><span>{e(k.replace("_"," ").title())}</span></div>' for k,v in p.get('scores',{}).items() if v is not None)
    specs=''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in p.get('specs',{}).items())
    good=''.join(f'<li>{e(x)}</li>' for x in p.get('good_for',[]))
    watch=''.join(f'<li>{e(x)}</li>' for x in p.get('watch_out',[]))
    s=p.get('signals',{}); signals=[]
    if s.get('rating') is not None: signals.append(f'⭐ {e(s["rating"])}/5')
    if s.get('rating_count'): signals.append(f'{e(s["rating_count"])} ratings')
    if s.get('price_checked') is not None: signals.append(f'Checked price ₹{e(s["price_checked"])}')
    signal_html=''.join(f'<span>{x}</span>' for x in signals)
    image=p.get('media',{}).get('image')
    media=f'<img src="/{e(image.lstrip("/"))}" alt="{e(p.get("media",{}).get("image_alt") or p["name"])}">' if image else '<div class="product-image-placeholder">Product visual</div>'
    verdict=e(p['verdict'].replace('_',' '))
    canonical=f'https://valueradar.in/products/{e(p["slug"])}/'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p.get('seo',{}).get('title') or p['name'])}</title><meta name="description" content="{e(p.get('seo',{}).get('description') or p['summary'])}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/product.css"><script async src="https://www.googletagmanager.com/gtag/js?id=G-BJC6CE45VZ"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-BJC6CE45VZ');</script></head><body><header class="site-header"><div class="container nav-wrap"><a class="brand" href="/"><span class="brand-mark">V</span><span><strong>ValueRadar</strong><small>Find Better. Pay Smarter.</small></span></a></div></header><main class="product-page"><div class="container"><nav class="breadcrumbs"><a href="/">Home</a><span>›</span><span>{e(p['category'])}</span><span>›</span><span>{e(p['id'])}</span></nav><section class="product-hero"><div class="product-media">{media}</div><div class="product-intro"><div class="product-meta"><span class="product-code">{e(p['id'])}</span><span class="product-verdict" data-verdict="{e(p['verdict'])}">{verdict}</span></div><h1>{e(p['name'])}</h1><p class="product-summary">{e(p['summary'])}</p><div class="signal-row">{signal_html}</div><div class="market-buttons">{market_buttons(p)}</div><p class="price-note">Prices, sellers and availability may change. Check the marketplace before buying.</p></div></section><section class="radar-score"><div><span class="eyebrow">VALUERADAR CHECK</span><h2>Our research snapshot</h2></div><div class="score-grid">{scores}</div></section><div class="product-columns"><section class="product-panel"><h2>Why we picked it</h2><p>{e(p['why_picked'])}</p></section><section class="product-panel"><h2>Good for</h2><ul>{good}</ul></section><section class="product-panel watch"><h2>Watch out</h2><ul>{watch}</ul></section><section class="product-panel"><h2>Key details</h2><dl class="spec-list">{specs}</dl></section></div><aside class="research-note"><strong>Research transparency</strong><p>Information checked {e(s.get('checked_at'))}. ValueRadar uses AI-assisted research to make shopping decisions easier; marketplace details can change.</p></aside></div></main><footer class="site-footer"><div class="container"><p>© ValueRadar India · <a href="/affiliate-disclosure.html">Affiliate Disclosure</a> · <a href="/privacy.html">Privacy</a> · <a href="/disclaimer.html">Disclaimer</a></p></div></footer><script>document.querySelectorAll('.market-btn').forEach(a=>a.addEventListener('click',()=>{{if(typeof gtag==='function')gtag('event','marketplace_click',{{marketplace:a.dataset.marketplace,vr_code:a.dataset.vrCode,link_url:a.href}})}}));</script></body></html>'''

def main():
    db=json.loads(DB.read_text(encoding='utf-8')); validate(db); OUT.mkdir(exist_ok=True)
    built=[]
    for p in db.get('products',[]):
        if p.get('status')!='published': continue
        d=OUT/p['slug']; d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(page(p),encoding='utf-8'); built.append(p['slug'])
    print(f'Built {len(built)} product page(s): '+(', '.join(built) if built else 'none'))
if __name__=='__main__': main()
