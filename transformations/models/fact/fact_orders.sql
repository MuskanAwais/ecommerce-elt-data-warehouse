{{
    config(
        materialized='table',
        tags=['fact'],
        description='Order facts table'
    )
}}

select
    {{ generate_surrogate_key(['order_id']) }} as order_key,
    order_id,
    dc.customer_key,
    so.customer_id,
    so.total,
    so.discountedTotal as discounted_total,
    (so.total - so.discountedTotal) as discount_amount,
    so.totalProducts as total_products,
    so.totalQuantity as total_quantity
from {{ ref('stg_orders') }} as so
left join {{ ref('dim_customer') }} as dc on so.customer_id = dc.customer_id
