-- Bronze Layer: Raw reviews ingestion
{{ config(materialized='table', schema='bronze') }}

SELECT
    listing_id,
    date,
    NULL AS reviewer_id,
    reviewer_name,
    comments,
    sentiment
FROM {{ source('raw', 'raw_reviews') }}
