{{
    config(
        materialized='table',
        tags=['dimension'],
        description='Customer dimension with business attributes'
    )
}}

select
    {{ generate_surrogate_key(['customer_id']) }} as customer_key,
    customer_id,
    name,
    email,
    city,
    gender
from {{ ref('stg_customers') }}
