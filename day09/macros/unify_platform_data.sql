{% macro unify_platform_data(platform_col, airbnb_value, booking_com_value, default_value=0) %}
/*
    Unify Platform Data Macro
    --------------------------
    Returns platform-specific values based on the platform column.
    Useful for handling platform-specific differences in data structure.

    Args:
        platform_col: Column containing platform name ('airbnb' or 'booking_com')
        airbnb_value: Value/expression to return for Airbnb
        booking_com_value: Value/expression to return for Booking.com
        default_value: Default value if platform doesn't match (optional)

    Returns:
        Platform-specific value

    Usage:
        {{  unify_platform_data(
                'platform',
                'guest_id',
                'guest_email',
                'unknown'
            ) }} AS unified_guest_id
*/

CASE {{ platform_col }}
    WHEN 'airbnb' THEN {{ airbnb_value }}
    WHEN 'booking_com' THEN {{ booking_com_value }}
    ELSE {{ default_value }}
END

{% endmacro %}
