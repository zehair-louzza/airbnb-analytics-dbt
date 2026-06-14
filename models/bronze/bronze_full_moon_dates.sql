-- Bronze Layer: Full moon dates seed ingestion
{{ config(materialized='table', schema='bronze') }}

SELECT
    CAST(full_moon_date AS DATE) AS full_moon_date
FROM {{ ref('full_moon_dates') }}
