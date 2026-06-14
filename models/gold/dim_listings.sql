-- Gold Layer: Dimension listings
-- Enrichi avec agregations depuis silver_reviews (nb d'avis + score sentiment moyen)
{{ config(materialized='table', schema='gold') }}

WITH review_agg AS (
    SELECT
        listing_id,
        COUNT(*) AS number_of_reviews,
        AVG(sentiment_score) AS avg_sentiment,
        SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_reviews,
        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_reviews,
        SUM(CASE WHEN sentiment = 'neutral'  THEN 1 ELSE 0 END) AS neutral_reviews,
        MIN(review_date) AS first_review,
        MAX(review_date) AS last_review
    FROM {{ ref('silver_reviews') }}
    GROUP BY listing_id
)

SELECT
    l.listing_id,
    l.listing_name,
    l.listing_url,
    l.host_id,
    h.host_name,
    h.is_superhost,
    l.room_type,
    l.price,
    l.minimum_nights,
    COALESCE(r.number_of_reviews, 0) AS number_of_reviews,
    r.avg_sentiment,
    r.positive_reviews,
    r.negative_reviews,
    r.neutral_reviews,
    -- Note proxy sur 5 derivee du sentiment moyen (de -1..1 vers 1..5)
    CASE
        WHEN r.avg_sentiment IS NULL THEN NULL
        ELSE ROUND( ((r.avg_sentiment + 1) / 2) * 4 + 1, 2)
    END AS review_scores_rating,
    r.first_review,
    r.last_review,
    l.created_at,
    l.updated_at
FROM {{ ref('silver_listings') }} l
LEFT JOIN {{ ref('silver_hosts') }} h
    ON l.host_id = h.host_id
LEFT JOIN review_agg r
    ON l.listing_id = r.listing_id
