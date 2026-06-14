-- Bronze Layer: Raw listings ingestion
{{ config(materialized='table', schema='bronze') }}

SELECT
    id,
    listing_url,
    name,
    room_type,
    minimum_nights,
    host_id,
    price,
    NULL AS neighbourhood_cleansed,
    NULL AS property_type,
    NULL AS accommodates,
    NULL AS bathrooms,
    bedrooms,
    NULL AS beds,
    NULL AS amenities,
    NULL AS number_of_reviews,
    NULL AS review_scores_rating,
    NULL AS latitude,
    NULL AS longitude,
    created_at,
    updated_at
FROM {{ source('raw', 'raw_listings') }}
