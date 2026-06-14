-- Bronze Layer: Raw listings ingestion
-- Source: data/raw/listings.csv (Inside Airbnb Berlin)
{{ config(materialized='table', schema='bronze') }}

SELECT
    id,
    listing_url,
    name,
    room_type,
    minimum_nights,
    host_id,
    price,
    created_at,
    updated_at
FROM {{ source('raw', 'raw_listings') }}
