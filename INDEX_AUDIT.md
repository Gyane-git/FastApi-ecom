# Database Index Audit & Recommendations

Database inspected read-only. **No indexes were added or modified.** The notes below are recommendations only — apply after measuring with `EXPLAIN` on real queries.

## Existing indexes (discovered)

| Table | Keys |
|---|---|
| products | PK `id`; unique `sku`, `slug`, `barcode`; `brand_id`, `category_id`, `name`, `price`, `rating`, `status` |
| brands | PK `id`; unique `slug`; `status` |
| categories | PK `id`; unique `slug`; `parent_id`, `level`, `status` |
| product_descriptions | PK `id`; unique (`product_id`,`language_code`); `product_id`, `language_code` |
| product_images | PK `id`; `product_id`, `(product_id, is_primary)` |
| product_prices | PK `id`; unique `(product_id, country_code, currency_code)`; `country_code`, `product_id` |
| product_reviews | PK `id`; `product_id`, `(product_id, rating)`, `user_id` |
| product_specifications | PK `id`; `product_id`, `specification_name` |
| product_variants | PK `id`; unique `sku`, `barcode`; `product_id`, `stock` |
| variant_attributes | PK `id`; `variant_id` |
| vendors | PK `id`; unique `slug`; `country_code`, `status` |
| vendor_products | PK `id`; unique `(vendor_id, product_id)`; `vendor_id`, `product_id` |

The base schema is already well indexed for the main access patterns.

## Recommended (not applied)

1. **Product search** — `q` currently uses `LIKE '%...%'` over `products.name`, `sku`, `slug`, plus brand/category name LIKE. This forces a full scan (~590ms locally). Add:
   ```sql
   ALTER TABLE products ADD FULLTEXT KEY idx_products_ft (name, sku, slug);
   ```
   and switch search to `MATCH ... AGAINST ...` for large catalogs. Thumbnails/specs can reuse existing indexes.

2. **Filtered listing** — common combos like `WHERE status=1 AND category_id=? ORDER BY created_at DESC` can scan many rows. Consider composite keys if profiling shows pain:
   ```sql
   ALTER TABLE products ADD KEY idx_products_status_cat_created (status, category_id, created_at);
   ALTER TABLE products ADD KEY idx_products_status_brand_created (status, brand_id, created_at);
   ```

3. **Price-sorted browse** — same pattern for `(status, price, id)`:
   ```sql
   ALTER TABLE products ADD KEY idx_products_status_price_id (status, price, id);
   ```

4. **Variant attribute facets** — filtering products by `attribute_name`/`attribute_value` joins through `variant_attributes`. Consider:
   ```sql
   ALTER TABLE variant_attributes ADD KEY idx_varattr_name_value (attribute_name, attribute_value);
   ```

5. **Brand/category name LIKE filters** — low cardinality LIKE is acceptable today (10k brands), monitor.

These are intentionally NOT created because they change the production schema. Run, review query plans, then apply deliberately.
