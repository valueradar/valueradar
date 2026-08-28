# ValueRadar build status

Updated: 2026-08-28

## Live after this batch is merged
- VR001 ATOM / Aliston kitchen scale
- VR002 AGARO Elite mini chopper
- VR003 NOVA NEC 1530 egg boiler
- VR004 Prestige PGMFB sandwich maker

## Automation foundation
- `products.json` is the product source of truth.
- `scripts/build_products.py` validates products, generates static SEO pages and generates the sitemap.
- Pull requests run catalogue validation through GitHub Actions.
- `scripts/check_catalogue.py` provides an additional generic integrity check for future expansion.

## Next revenue milestones
1. Grow to at least 10 defensible product/review pages.
2. Build recurring social creatives around VR codes and route traffic through valueradar.in.
3. Measure product-page and marketplace-click behaviour in GA4.
4. Enrol in affiliate programs when the site/content footprint is ready.
5. Replace normal marketplace URLs with compliant affiliate URLs only after approval.
