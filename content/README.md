# ValueRadar content pipeline

`products.json` is the source of truth for researched product records.

Workflow:
1. Research and verify a candidate.
2. Add a conservative record to `products.json`.
3. Run `python scripts/build_products.py` to validate records, generate published product pages and rebuild `sitemap.xml`.
4. Review the generated pages and marketplace links.
5. Merge through a pull request.

Price language:
- `price_context: third_party_tracker` → **Tracked reference price**
- `price_context: marketplace_observed` → **Marketplace price observed**

Never convert a marketplace discount badge into `GENUINE_DEAL` without independent historical-price evidence.
