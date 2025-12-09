{{
  config(
    materialized='incremental',
    unique_key='day09_event_id',
    on_schema_change='append_new_columns',
    tags=['marts', 'facts', 'incremental']
  )
}}

/*
    Funnel Conversion Fact Table (INCREMENTAL)
    -------------------------------------------
    Tracks all funnel events with conversion metrics.
    Incremental model that only processes new events on subsequent runs.

    Funnel stages: inquiry → booking → check_in → check_out → review

    Production-ready pattern:
    - Only new events (based on event_timestamp) are added on incremental runs
    - Existing events are not re-processed
    - Supports efficient daily/hourly updates
*/

WITH funnel_events AS (
    SELECT * FROM {{ ref('int_funnel_events') }}

    {% if is_incremental() %}
    -- On incremental runs, only process events newer than the latest event in the table
    WHERE day09_event_timestamp > (SELECT MAX(day09_event_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    day09_event_id,
    day09_platform,
    day09_guest_id,
    day09_property_id,
    day09_event_timestamp,
    day09_stage,
    day09_booking_id,
    day09_final_booking_value,
    day09_days_to_next_stage,
    day09_converted_to_next_stage,

    -- Additional time-based fields for analysis
    DATE(day09_event_timestamp) AS day09_event_date,
    CAST(STRFTIME('%Y', day09_event_timestamp) AS INTEGER) AS day09_event_year,
    CAST(STRFTIME('%m', day09_event_timestamp) AS INTEGER) AS day09_event_month,
    CAST(STRFTIME('%w', day09_event_timestamp) AS INTEGER) AS day09_event_day_of_week,

    -- Stage ordering for funnel analysis
    CASE day09_stage
        WHEN 'inquiry' THEN 1
        WHEN 'booking' THEN 2
        WHEN 'check_in' THEN 3
        WHEN 'check_out' THEN 4
        WHEN 'review' THEN 5
        ELSE 0
    END AS day09_stage_order

FROM funnel_events
