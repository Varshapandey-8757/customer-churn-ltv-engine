-- =============================================================================
-- SQL Transformation: int_customer_segmentation.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Segments customers based on Monetary Value, Churn Risk Profile, 
--   Tenure Maturity, and LTV Potential to produce strategic business cohorts.
-- =============================================================================

WITH customer_features AS (
    SELECT * FROM {{ ref('int_customer_features') }} -- or int_customer_features table/view
)

SELECT
    customer_id,
    tenure_months,
    tenure_cohort,
    monthly_charges,
    total_charges,
    contract_type,
    is_month_to_month,
    payment_method,
    is_autopay_enabled,
    total_services_count,
    has_fiber_no_techsupport_risk,
    is_churned,

    -- -------------------------------------------------------------------------
    -- 1. Value Tier Segmentation
    -- -------------------------------------------------------------------------
    CASE 
        WHEN monthly_charges >= 80.0 THEN 'High Value'
        WHEN monthly_charges >= 40.0 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS value_tier,

    -- -------------------------------------------------------------------------
    -- 2. Behavioral Risk Segmentation
    -- -------------------------------------------------------------------------
    CASE 
        WHEN is_month_to_month = 1 AND (tenure_months <= 12 OR has_fiber_no_techsupport_risk = 1 OR payment_method = 'Electronic check') 
            THEN 'High Risk'
        WHEN (contract_type IN ('One year', 'Two year') AND is_autopay_enabled = 1) OR tenure_months >= 36 
            THEN 'Low Risk'
        ELSE 'Moderate Risk'
    END AS risk_profile,

    -- -------------------------------------------------------------------------
    -- 3. Strategic Action Segment (Value vs Risk Matrix)
    -- -------------------------------------------------------------------------
    CASE 
        WHEN monthly_charges >= 80.0 AND (is_month_to_month = 1 OR has_fiber_no_techsupport_risk = 1) 
            THEN 'High Value - Urgent Retention'
        WHEN monthly_charges >= 80.0 
            THEN 'High Value - Loyal VIP'
        WHEN monthly_charges < 40.0 AND is_month_to_month = 1 
            THEN 'Low Value - Price Sensitive'
        ELSE 'Core Mid-Market'
    END AS customer_strategic_segment,

    -- -------------------------------------------------------------------------
    -- 4. Customer Lifetime Value (LTV) Proxy Estimation
    -- -------------------------------------------------------------------------
    total_charges AS historical_ltv,
    
    -- Heuristic projected remaining life in months based on contract commitments
    CASE 
        WHEN contract_type = 'Two year' THEN 24
        WHEN contract_type = 'One year' THEN 12
        WHEN is_month_to_month = 1 AND tenure_months <= 6 THEN 3
        WHEN is_month_to_month = 1 AND tenure_months <= 18 THEN 6
        ELSE 12
    END AS estimated_remaining_months,

    ROUND(
        total_charges + (
            monthly_charges * 
            CASE 
                WHEN contract_type = 'Two year' THEN 24
                WHEN contract_type = 'One year' THEN 12
                WHEN is_month_to_month = 1 AND tenure_months <= 6 THEN 3
                WHEN is_month_to_month = 1 AND tenure_months <= 18 THEN 6
                ELSE 12
            END
        ), 2
    ) AS estimated_total_ltv

FROM customer_features;
