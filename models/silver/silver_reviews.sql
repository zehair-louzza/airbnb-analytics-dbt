{{ config(materialized='table', schema='silver') }}

SELECT
    CAST(listing_id AS INTEGER) AS listing_id,
    CAST(date AS DATE) AS review_date,
    NULL AS reviewer_id,
    reviewer_name,
    comments AS review_text,
    sentiment
FROM {{ ref('bronze_reviews') }}
WHERE comments IS NOT NULL
  AND TRIM(comments) != ''
ORDER BY date ASC
