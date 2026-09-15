-- =============================================================================
-- SQL Transformation: fct_churn_ltv_features.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Consolidated, model-ready feature table combining customer demographics,
--   tenure metrics, charge velocity, service bundles, behavioral segmentation,
--   and LTV proxies. Fed directly into Churn (classification) and LTV (regression) models.
-- =============================================================================

WITH features AS (
    SELECT * FROM {{ ref('int_customer_features') }}
),
segments AS (
    SELECT 
        customer_id,
        value_tier,
        risk_profile,
        customer_strategic_segment,
        historical_ltv,
        estimated_remaining_months,
        estimated_total_ltv
    FROM {{ ref('int_customer_segmentation') }}
)

SELECT
    f.customer_id,
    
    -- Demographics
    f.gender,
    f.is_senior_citizen,
    f.has_partner,
    f.has_dependents,
    
    -- Tenure & Lifecycle
    f.tenure_months,
    f.tenure_years,
    f.tenure_cohort,
    f.is_new_customer,
    
    -- Financial & Charge Features
    f.monthly_charges,
    f.total_charges,
    f.expected_cumulative_charges,
    f.charges_ratio,
    f.avg_historical_monthly_charge,
    f.charge_velocity,
    f.monthly_charge_tier,
    
    -- Contract & Billing
    f.contract_type,
    f.contract_term_months,
    f.is_month_to_month,
    f.payment_method,
    f.is_autopay_enabled,
    f.is_paperless_billing,
    f.has_paperless_manual_payment_risk,
    
    -- Service Usage & Bundles
    f.has_phone_service,
    f.has_multiple_lines,
    f.has_internet_service,
    f.internet_service_type,
    f.has_online_security,
    f.has_online_backup,
    f.has_device_protection,
    f.has_tech_support,
    f.has_streaming_tv,
    f.has_streaming_movies,
    f.total_services_count,
    f.has_streaming_bundle,
    f.has_security_bundle,
    f.has_fiber_no_techsupport_risk,
    
    -- Strategic Segmentation & Value Tiers
    s.value_tier,
    s.risk_profile,
    s.customer_strategic_segment,
    
    -- LTV Target & Proxies
    s.historical_ltv,
    s.estimated_remaining_months,
    s.estimated_total_ltv,
    
    -- Churn Targets
    f.churn_label,
    f.is_churned

FROM features f
INNER JOIN segments s ON f.customer_id = s.customer_id;
