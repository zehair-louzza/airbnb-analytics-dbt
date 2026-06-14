-- Bronze Layer: Raw hosts ingestion
{{ config(materialized='table', schema='bronze') }}

SELECT
    id,
    name,
    is_superhost,
    created_at,
    updated_at
FROM {{ source('raw', 'raw_hosts') }}
