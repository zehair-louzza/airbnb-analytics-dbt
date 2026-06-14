-- Silver Layer: Full moon dates transformation
{{ config(materialized='table', schema='silver') }}

SELECT
    full_moon_date,
    CAST(full_moon_date AS DATE) + INTERVAL 1 DAY AS full_moon_date_plus_1
FROM {{ ref('bronze_full_moon_dates') }}
