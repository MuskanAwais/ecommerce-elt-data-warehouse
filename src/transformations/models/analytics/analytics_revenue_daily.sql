{{
    config(
        materialized='table',
        description='Daily total revenue aggregation',
        tags=['analytics']
    )
}}

with daily_revenue as (
    select
        date_trunc('day', order_date) as report_date,
        sum(discounted_total) as daily_revenue
    from {{ ref('fact_orders') }}
    group by 1
)
select * from daily_revenue
