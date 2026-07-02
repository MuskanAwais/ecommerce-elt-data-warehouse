{{
    config(
        materialized='table',
        tags=['dimension'],
        description='Product dimension with business attributes'
    )
}}

select
    {{ generate_surrogate_key(['product_id']) }} as product_key,
    product_id,
    title,
    description,
    category,
    price,
    discount_percentage,
    rating,
    stock,
    brand,
    sku,
    case
        when stock > 10 then 'In Stock'
        when stock > 0 then 'Low Stock'
        else 'Out of Stock'
    end as stock_status
from {{ ref('stg_products') }}
