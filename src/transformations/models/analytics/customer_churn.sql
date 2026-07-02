{{
    config(
        materialized='table',
        tags=['metrics'],
        description='Customer churn and retention analysis'
    )
}}

select
    dc.customer_key,
    sc.name,
    sc.email,
    count(distinct fo.order_id) as total_orders,
    min(current_date) as first_order_date,
    max(current_date) as last_order_date,
    sum(fo.discounted_total) as lifetime_value,
    case
        when count(distinct fo.order_id) = 0 then 'Never Purchased'
        when (current_date - max(current_date)) > 90 then 'Churned'
        when (current_date - max(current_date)) > 30 then 'At Risk'
        else 'Active'
    end as customer_status
from {{ ref('stg_customers') }} as sc
left join {{ ref('dim_customer') }} as dc on sc.customer_id = dc.customer_id
left join {{ ref('fact_orders') }} as fo on dc.customer_key = fo.customer_key
group by dc.customer_key, sc.name, sc.email
