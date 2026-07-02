{{
    config(
        materialized='view',
        alias='raw_products',
        tags=['staging'],
        description='Staging view for products - unnested from raw array'
    )
}}

select distinct
    product.id as product_id,
    product.title,
    product.description,
    product.category,
    product.price,
    product.discountPercentage as discount_percentage,
    product.rating,
    product.stock,
    product.brand,
    product.sku
from {{ source('raw','stg_products') }}
cross join unnest(products) as t(product)
