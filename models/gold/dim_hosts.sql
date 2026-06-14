-- Gold Layer: Dimension hosts
-- Enrichi avec nb d'annonces par hote et flag multi-annonces
{{ config(materialized='table', schema='gold') }}

WITH listing_agg AS (
    SELECT
        host_id,
        COUNT(*) AS total_listings,
        AVG(price) AS avg_price,
        SUM(number_of_reviews) AS total_reviews
    FROM {{ ref('dim_listings') }}
    GROUP BY host_id
)

SELECT
    h.host_id,
    COALESCE(h.host_name, 'Anonymous') AS host_name,
    h.is_superhost,
    h.host_since,
    h.updated_at,
    COALESCE(la.total_listings, 0) AS total_listings,
    la.avg_price,
    la.total_reviews,
    CASE WHEN COALESCE(la.total_listings, 0) > 1 THEN TRUE ELSE FALSE END AS is_multi_host
FROM {{ ref('silver_hosts') }} h
LEFT JOIN listing_agg la
    ON h.host_id = la.host_id
