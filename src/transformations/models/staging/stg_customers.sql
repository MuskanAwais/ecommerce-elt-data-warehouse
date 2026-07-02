{{
    config(
        materialized='view',
        alias='raw_customers',
        tags=['staging'],
        description='Staging view for customers - unnested from raw array'
    )
}}

select distinct
    user.id as customer_id,
    user.firstName || ' ' || user.lastName as name,
    user.email,
    user.phone,
    user.username,
    user.gender,
    (user.address).city as city
from {{ source('raw','stg_customers') }}
cross join unnest(users) as t(user)
