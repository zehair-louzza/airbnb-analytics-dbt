-- Gold Layer: Fact reviews
-- Avis non-null tries par date avec jointure aux listings et hosts
{{ config(materialized='table', schema='gold') }}

SELECT
    r.listing_id,
    r.review_date,
    r.reviewer_id,
    r.reviewer_name,
    r.review_text,
    l.listing_name,
    l.room_type,
    l.neighbourhood,
    l.price,
    h.host_name,
    h.is_superhost
FROM {{ ref('silver_reviews') }} r
INNER JOIN {{ ref('dim_listings') }} l
    ON r.listing_id = l.listing_id
INNER JOIN {{ ref('silver_hosts') }} h
    ON l.host_id = h.host_id
WHERE r.review_text IS NOT NULL
ORDER BY r.review_date ASC
