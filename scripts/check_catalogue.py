#!/usr/bin/env python3
import html
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
db=json.loads((root/'products.json').read_text(encoding='utf-8'))
errors=[]
published=[p for p in db['products'] if p.get('status')=='published']
for p in published:
    page=root/'products'/p['slug']/'index.html'
    if not page.exists():
        errors.append(f"missing page: {p['id']} {page}")
    else:
        text=page.read_text(encoding='utf-8')
        needles=(p['id'], html.escape(p['name'], quote=True), 'G-BJC6CE45VZ')
        for needle in needles:
            if needle not in text:
                errors.append(f"{p['id']}: generated page missing {needle}")
sitemap=(root/'sitemap.xml').read_text(encoding='utf-8')
for p in published:
    url=f"https://valueradar.in/products/{p['slug']}/"
    if url not in sitemap:
        errors.append(f"sitemap missing {p['id']}")
if errors:
    raise SystemExit('Catalogue check failed:\n- '+'\n- '.join(errors))
print(f"Catalogue OK: {len(published)} published products")
