-- Churn Report
-- Returns number of churned customers per month
SELECT
  DATE_TRUNC('month', churn_date) AS churn_month,
  COUNT(DISTINCT customer_id) AS churned_customers
FROM {{ ref('dim_customer') }} c
JOIN {{ ref('fact_churn') }} f ON c.customer_key = f.customer_key
WHERE f.is_churn = TRUE
GROUP BY 1
ORDER BY 1;
