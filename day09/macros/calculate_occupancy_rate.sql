{% macro calculate_occupancy_rate(nights_booked_col, nights_available_col) %}
/*
    Calculate Occupancy Rate Macro
    -------------------------------
    Calculates the occupancy rate percentage for a property.

    Formula: (nights booked / nights available) × 100

    Args:
        nights_booked_col: Column containing total nights booked
        nights_available_col: Column containing total nights available

    Returns:
        Occupancy rate as a percentage (0-100)

    Usage:
        {{ calculate_occupancy_rate('total_nights_booked', 'nights_available') }} AS occupancy_rate_pct
*/

ROUND(
    100.0 * {{ nights_booked_col }} / NULLIF({{ nights_available_col }}, 0),
    2
)

{% endmacro %}
