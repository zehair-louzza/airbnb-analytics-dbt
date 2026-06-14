-- Gold Layer: Fact reviews
-- Avis enrichis avec infos listings et hosts
{{ config(materialized='table', schema='gold') }}

SELECT
    r.listing_id,
    r.review_date,
    r.reviewer_name,
    r.review_text,
    r.sentiment,
    r.sentiment_score,
    l.listing_name,
    l.room_type,
    l.price,
    h.host_name,
    h.is_superhost
FROM {{ ref('silver_reviews') }} r
INNER JOIN {{ ref('silver_listings') }} l
    ON r.listing_id = l.listing_id
LEFT JOIN {{ ref('silver_hosts') }} h
    ON l.host_id = h.host_id
