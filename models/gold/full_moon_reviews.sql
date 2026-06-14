-- Gold Layer: Full moon reviews
-- Avis emis le jour de pleine lune ou J+1
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
    fmd.full_moon_date,
    TRUE AS is_full_moon_review
FROM {{ ref('silver_reviews') }} r
INNER JOIN {{ ref('silver_full_moon_dates') }} fmd
    ON r.review_date BETWEEN fmd.full_moon_date AND fmd.full_moon_date_plus_1
INNER JOIN {{ ref('silver_listings') }} l
    ON r.listing_id = l.listing_id
