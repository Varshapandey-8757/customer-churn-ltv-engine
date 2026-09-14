-- =============================================================================
-- SQL Transformation: int_customer_features.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Transforms staged customer & subscription data into intermediate 
--   engineered features covering tenure cohorts, charge ratios, service bundling, 
--   and behavioral risk flags.
-- =============================================================================

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }} -- or stg_customers table/view
),
subscriptions AS (
    SELECT * FROM {{ ref('stg_subscriptions') }} -- or stg_subscriptions table/view
)

SELECT
    c.customer_id,
    
    -- Demographics
    c.gender,
    c.is_senior_citizen,
    c.has_partner,
    c.has_dependents,
    
    -- -------------------------------------------------------------------------
    -- 1. Tenure Features
    -- -------------------------------------------------------------------------
    c.tenure_months,
    ROUND(CAST(c.tenure_months AS FLOAT) / 12.0, 2) AS tenure_years,
    CASE 
        WHEN c.tenure_months <= 6 THEN '0-6m [New]'
        WHEN c.tenure_months <= 12 THEN '7-12m [Adopter]'
        WHEN c.tenure_months <= 24 THEN '13-24m [Established]'
        WHEN c.tenure_months <= 48 THEN '25-48m [Mature]'
        ELSE '49+m [Veteran]'
    END AS tenure_cohort,
    CASE WHEN c.tenure_months <= 6 THEN 1 ELSE 0 END AS is_new_customer,
    
    -- -------------------------------------------------------------------------
    -- 2. Charges & Financial Metrics
    -- -------------------------------------------------------------------------
    c.monthly_charges,
    c.total_charges,
    ROUND(CAST(c.tenure_months * c.monthly_charges AS DECIMAL(10, 2)), 2) AS expected_cumulative_charges,
    CASE 
        WHEN c.tenure_months = 0 OR c.monthly_charges = 0 THEN 1.0
        ELSE ROUND(CAST(c.total_charges / (c.tenure_months * c.monthly_charges) AS DECIMAL(10, 4)), 4)
    END AS charges_ratio,
    ROUND(CAST(c.total_charges / (c.tenure_months + 1.0) AS DECIMAL(10, 2)), 2) AS avg_historical_monthly_charge,
    ROUND(CAST(c.monthly_charges - (c.total_charges / (c.tenure_months + 1.0)) AS DECIMAL(10, 2)), 2) AS charge_velocity,
    CASE 
        WHEN c.monthly_charges < 35.0 THEN 'Low (<$35)'
        WHEN c.monthly_charges < 70.0 THEN 'Medium ($35-$70)'
        WHEN c.monthly_charges < 90.0 THEN 'High ($70-$90)'
        ELSE 'Premium (>$90)'
    END AS monthly_charge_tier,
    
    -- -------------------------------------------------------------------------
    -- 3. Contract & Payment Friction Features
    -- -------------------------------------------------------------------------
    s.contract_type,
    s.contract_term_months,
    CASE WHEN s.contract_type = 'Month-to-month' THEN 1 ELSE 0 END AS is_month_to_month,
    s.payment_method,
    s.is_autopay_enabled,
    s.is_paperless_billing,
    CASE 
        WHEN s.is_paperless_billing = 1 AND s.is_autopay_enabled = 0 THEN 1 
        ELSE 0 
    END AS has_paperless_manual_payment_risk,
    
    -- -------------------------------------------------------------------------
    -- 4. Service Usage & Bundling Features
    -- -------------------------------------------------------------------------
    s.has_phone_service,
    s.has_multiple_lines,
    s.has_internet_service,
    s.internet_service_type,
    s.has_online_security,
    s.has_online_backup,
    s.has_device_protection,
    s.has_tech_support,
    s.has_streaming_tv,
    s.has_streaming_movies,
    
    -- Total count of add-on services adopted
    (
        s.has_phone_service + 
        s.has_multiple_lines + 
        s.has_online_security + 
        s.has_online_backup + 
        s.has_device_protection + 
        s.has_tech_support + 
        s.has_streaming_tv + 
        s.has_streaming_movies
    ) AS total_services_count,
    
    -- Service bundles
    CASE WHEN s.has_streaming_tv = 1 AND s.has_streaming_movies = 1 THEN 1 ELSE 0 END AS has_streaming_bundle,
    CASE WHEN s.has_online_security = 1 AND s.has_tech_support = 1 THEN 1 ELSE 0 END AS has_security_bundle,
    
    -- Key Churn Risk Interaction: High-bandwidth Fiber Optic without Tech Support
    CASE 
        WHEN s.internet_service_type = 'Fiber optic' AND s.has_tech_support = 0 THEN 1 
        ELSE 0 
    END AS has_fiber_no_techsupport_risk,
    
    -- -------------------------------------------------------------------------
    -- 5. Targets / Labels
    -- -------------------------------------------------------------------------
    c.churn_label,
    c.is_churned

FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id;
