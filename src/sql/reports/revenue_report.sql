-- Revenue Report
-- Returns total revenue by day
SELECT
  DATE_TRUNC('day', order_timestamp) AS revenue_date,
  SUM(total_amount) AS daily_revenue
FROM {{ ref('fact_sales') }}
GROUP BY 1
ORDER BY 1;
