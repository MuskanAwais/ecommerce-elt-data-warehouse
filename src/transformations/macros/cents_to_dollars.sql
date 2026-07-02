{#
    Convert an integer amount in cents to dollars as a decimal string.
#}
{% macro cents_to_dollars(cents) %}
    ({{ cents }} / 100.0)
{% endmacro %}
