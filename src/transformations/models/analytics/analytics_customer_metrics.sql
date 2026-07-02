{{
    config(
        materialized='table',
        description='Customer churn and LTV metrics',
        tags=['analytics']
    )
}}

with customer_orders as (
    select
        dc.customer_key,
        sc.name,
        sc.email,
        count(distinct fo.order_id) as total_orders,
        min(fo.order_date) as first_order_date,
        max(fo.order_date) as last_order_date,
        sum(fo.discounted_total) as lifetime_value
    from {{ ref('stg_customers') }} as sc
    left join {{ ref('dim_customer') }} as dc on sc.customer_id = dc.customer_id
    left join {{ ref('fact_orders') }} as fo on dc.customer_key = fo.customer_key
    group by dc.customer_key, sc.name, sc.email
)

select
    customer_key,
    name,
    email,
    total_orders,
    first_order_date,
    last_order_date,
    lifetime_value,
    case
        when total_orders = 0 then 'Never Purchased'
        when datediff('day', last_order_date, current_date) > 90 then 'Churned'
        when datediff('day', last_order_date, current_date) > 30 then 'At Risk'
        else 'Active'
    end as customer_status
from customer_orders
