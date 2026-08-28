# ValueRadar analytics funnel

Primary funnel:

social/search visit → product page → marketplace click → affiliate order → commission

## GA4 events already used
- `page_view` — automatic
- `site_search` — ValueRadar search terms
- `category_interest` — homepage category intent
- `marketplace_click` — outbound shopping click with marketplace, link URL and VR code

## Decision metrics
For each VR code track:
1. Product page views
2. Marketplace clicks
3. Marketplace click-through rate
4. Traffic source/campaign
5. Affiliate ordered items and commission once affiliate reporting is available

Do not optimize primarily for social views. Prioritize qualified ValueRadar visits, marketplace CTR and eventual commission per product/page.
