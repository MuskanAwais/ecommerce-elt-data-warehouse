{#
    Generate a deterministic surrogate key from a list of column names.
    Uses MD5 hash for consistent key generation across runs.
    
    Usage:
        {{ generate_surrogate_key(['column1', 'column2']) }}
    
    Returns:
        A hashed string suitable for use as a primary key
#}
{% macro generate_surrogate_key(column_names) %}
    md5(cast(concat({% for col in column_names %}cast({{ col }} as varchar){% if not loop.last %}, '-', {% endif %}{% endfor %}) as varchar))
{% endmacro %}
