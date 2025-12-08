-- Day 08 - Macro: Calculate Activation Time
-- Reusable macro to calculate days from signup to activation

{% macro calculate_activation_time(event_date_col, signup_date_col) %}
    julianday({{ event_date_col }}) - julianday({{ signup_date_col }})
{% endmacro %}


{% macro days_between(start_date_col, end_date_col) %}
    julianday({{ end_date_col }}) - julianday({{ start_date_col }})
{% endmacro %}


{% macro cohort_month(date_col) %}
    date({{ date_col }}, 'start of month')
{% endmacro %}
