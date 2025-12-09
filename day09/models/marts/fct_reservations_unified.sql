{{
  config(
    materialized='table',
    tags=['marts', 'facts']
  )
}}

/*
    Unified Reservations Fact Table
    --------------------------------
    Final fact table combining all reservation data from both platforms.
    This table powers:
    - Portfolio metrics calculations
    - Platform performance analysis
    - Revenue reporting
    - Occupancy rate calculations
*/

SELECT
    day09_booking_id,
    day09_platform,
    day09_guest_id,
    day09_property_id,
    day09_booking_timestamp,
    day09_check_in_date,
    day09_check_out_date,
    day09_num_guests,
    day09_nights,
    day09_nightly_rate,
    day09_total_price,
    day09_platform_fee,
    day09_net_revenue,
    day09_status,
    day09_adr,
    day09_lead_time_days,
    day09_length_of_stay,
    day09_check_in_month,

    -- Additional calculated fields for analysis
    ROUND((day09_platform_fee / day09_total_price) * 100, 2) AS day09_platform_fee_pct,
    DATE(day09_booking_timestamp) AS day09_booking_date,
    CAST(STRFTIME('%Y', day09_check_in_date) AS INTEGER) AS day09_check_in_year,
    CAST(STRFTIME('%m', day09_check_in_date) AS INTEGER) AS day09_check_in_month_num,
    CAST(STRFTIME('%w', day09_check_in_date) AS INTEGER) AS day09_check_in_day_of_week

FROM {{ ref('int_unified_reservations') }}
WHERE day09_status IN ('confirmed', 'completed')  -- Only active reservations
