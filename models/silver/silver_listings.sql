{{ config(materialized='view') }}


SELECT
    id AS listing_id,
    listing_url,
    name AS listing_name,
    CAST(host_id AS INTEGER) AS host_id,
    room_type,
    NULL AS neighbourhood_cleansed,
    NULL AS property_type,
    NULL AS accommodates,
    CAST(bedrooms AS INTEGER) AS bedrooms,
    NULL AS beds,
    CAST(REPLACE(REPLACE(CAST(price AS VARCHAR),'$',''),',','') AS FLOAT) AS price_clean,
    CASE WHEN CAST(minimum_nights AS INTEGER)>30 THEN 30 ELSE CAST(minimum_nights AS INTEGER) END AS minimum_nights,
    NULL AS number_of_reviews,
    NULL AS review_scores_rating,
    NULL AS latitude,
    NULL AS longitude,
    created_at,
    updated_at
FROM {{ ref('bronze_listings') }}