-- Gold Layer: Dimension listings
{{ config(materialized='table', schema='gold') }}

SELECT
    l.listing_id,
    l.listing_name,
    l.listing_url,
    l.host_id,
    h.host_name,
    l.room_type,
    l.neighbourhood_cleansed AS neighbourhood,
    l.property_type,
    l.accommodates,
    l.bedrooms,
    l.beds,
    l.price_clean AS price,
    l.minimum_nights,
    l.number_of_reviews,
    l.review_scores_rating
FROM {{ ref('silver_listings') }} l
LEFT JOIN {{ ref('silver_hosts') }} h
    ON l.host_id = h.host_id
