-- Gold Layer: Dimension hosts
-- Hotes avec valeurs nulles remplacees

{{ config(materialized='table', schema='gold') }}

SELECT
    host_id,
    COALESCE(host_name, 'Anonymous')    AS host_name,
    is_superhost,
    host_since,
    updated_at
FROM {{ ref('silver_hosts') }}
