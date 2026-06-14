-- Gold Layer: Full moon reviews
-- Reviews matching full moon dates
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
    fmd.full_moon_date,
    TRUE AS is_full_moon_review
FROM {{ ref('silver_reviews') }} r
INNER JOIN {{ ref('silver_full_moon_dates') }} fmd
    ON r.review_date >= fmd.full_moon_date
    AND r.review_date <= fmd.full_moon_date + INTERVAL 1 DAY
INNER JOIN {{ ref('dim_listings') }} l
    ON r.listing_id = l.listing_id
ORDER BY r.review_date ASC
