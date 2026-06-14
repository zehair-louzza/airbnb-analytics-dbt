-- Silver Layer: Hosts transformation
-- Nettoyage et typage des donnees des hotes

{{ config(materialized='table', schema='silver') }}

SELECT
    CAST(id AS INTEGER)         AS host_id,
    COALESCE(name, 'Anonymous')      AS host_name,
    CASE
        WHEN is_superhost = 't' THEN TRUE
        ELSE FALSE
    END                          AS is_superhost,
    CAST(created_at AS DATE)    AS host_since,
    CAST(updated_at AS DATE)    AS updated_at
FROM {{ ref('bronze_hosts') }}
