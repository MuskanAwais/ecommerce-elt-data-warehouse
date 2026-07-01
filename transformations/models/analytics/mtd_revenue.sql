{{
    config(
        materialized='table',
        tags=['metrics'],
        description='Month-to-date revenue metrics'
    )
}}

select
    date_trunc('month', current_date) as month,
    current_date as report_date,
    count(distinct order_id) as total_orders,
    count(distinct customer_id) as unique_customers,
    sum(total) as gross_revenue,
    sum(discount_amount) as total_discounts,
    sum(discounted_total) as net_revenue,
    round(sum(discounted_total) / count(distinct order_id), 2) as avg_order_value
from {{ ref('fact_orders') }}
