{{
    config(
        materialized='view',
        alias='raw_orders',
        tags=['staging'],
        description='Staging view for orders - unnested from raw array'
    )
}}

select distinct
    cart.id as order_id,
    cart.userId as customer_id,
    cart.total,
    cart.discountedTotal,
    cart.totalProducts,
    cart.totalQuantity
from {{ source('raw','stg_orders') }}
cross join unnest(carts) as t(cart)
