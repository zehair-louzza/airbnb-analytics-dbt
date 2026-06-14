-- Bronze Layer: Raw reviews ingestion
-- Source: data/raw/reviews.csv (Inside Airbnb Berlin)
{{ config(materialized='table', schema='bronze') }}

SELECT
    listing_id,
    date,
    reviewer_name,
    comments,
    sentiment
FROM {{ source('raw', 'raw_reviews') }}
