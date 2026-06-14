-- Silver Layer: Listings transformation
-- Nettoyage prix, cast types, filtrage valeurs aberrantes
{{ config(materialized='table', schema='silver') }}

SELECT
    CAST(id AS INTEGER) AS listing_id,
    listing_url,
    name AS listing_name,
    CAST(host_id AS INTEGER) AS host_id,
    room_type,
    -- Nettoyage prix : retire le symbole $ et la virgule de millier
    TRY_CAST(REPLACE(REPLACE(CAST(price AS VARCHAR), '$', ''), ',', '') AS DOUBLE) AS price,
    -- Capping des nuits minimum aberrantes
    CASE
        WHEN CAST(minimum_nights AS INTEGER) > 30 THEN 30
        WHEN CAST(minimum_nights AS INTEGER) < 1 THEN 1
        ELSE CAST(minimum_nights AS INTEGER)
    END AS minimum_nights,
    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at
FROM {{ ref('bronze_listings') }}
WHERE price IS NOT NULL
  AND room_type IS NOT NULL
