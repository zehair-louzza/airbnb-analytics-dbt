-- Silver Layer: Reviews transformation
-- Standardisation dates, conservation du sentiment
{{ config(materialized='table', schema='silver') }}

SELECT
    CAST(listing_id AS INTEGER) AS listing_id,
    CAST(date AS DATE) AS review_date,
    reviewer_name,
    comments AS review_text,
    LOWER(TRIM(sentiment)) AS sentiment,
    CASE
        WHEN LOWER(TRIM(sentiment)) = 'positive' THEN 1
        WHEN LOWER(TRIM(sentiment)) = 'neutral'  THEN 0
        WHEN LOWER(TRIM(sentiment)) = 'negative' THEN -1
        ELSE NULL
    END AS sentiment_score
FROM {{ ref('bronze_reviews') }}
WHERE comments IS NOT NULL
  AND TRIM(comments) != ''
  AND date IS NOT NULL
