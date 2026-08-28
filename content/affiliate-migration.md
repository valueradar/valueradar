# Affiliate link migration procedure

After program approval:
1. Generate the affiliate URL using the marketplace's approved tools/API.
2. Replace only the corresponding marketplace URL in `products.json`.
3. Set that marketplace object's `affiliate` flag to `true`.
4. Rebuild product pages so the outbound link receives `rel="sponsored"`.
5. Confirm the required disclosure language is visible and accurate.
6. Test `marketplace_click` after migration.
7. Never fabricate tracking parameters or tags.
