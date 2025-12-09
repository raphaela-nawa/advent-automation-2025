{% macro calculate_stage_duration(timestamp_col, stage_col, partition_col) %}
/*
    Calculate Stage Duration Macro
    -------------------------------
    Calculates the time spent in each funnel stage using window functions.

    Args:
        timestamp_col: Column containing event timestamp
        stage_col: Column containing stage name
        partition_col: Column to partition by (usually guest_id or booking_id)

    Returns:
        Duration in hours between stages

    Usage:
        {{ calculate_stage_duration('event_timestamp', 'stage', 'guest_id') }}
*/

(
    JULIANDAY({{ timestamp_col }}) -
    JULIANDAY(LAG({{ timestamp_col }}) OVER (
        PARTITION BY {{ partition_col }}, {{ stage_col }}
        ORDER BY {{ timestamp_col }}
    ))
) * 24  -- Convert days to hours

{% endmacro %}
