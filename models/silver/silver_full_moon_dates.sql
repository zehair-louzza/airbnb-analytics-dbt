-- Silver Layer: Full moon dates with J+1
{{ config(materialized='table', schema='silver') }}

SELECT
    full_moon_date,
    full_moon_date + INTERVAL 1 DAY AS full_moon_date_plus_1
FROM {{ ref('bronze_full_moon_dates') }}
