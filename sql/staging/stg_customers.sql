-- =============================================================================
-- SQL Staging: stg_customers.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Ingests raw telecommunications data, casts column types, sanitizes 
--   TotalCharges (handling empty strings and zero-tenure rows), and formats 
--   demographic flags and churn outcome targets.
-- =============================================================================

SELECT
    customerID AS customer_id,
    gender,
    CAST(SeniorCitizen AS INTEGER) AS is_senior_citizen,
    CASE WHEN Partner = 'Yes' THEN 1 ELSE 0 END AS has_partner,
    CASE WHEN Dependents = 'Yes' THEN 1 ELSE 0 END AS has_dependents,
    CAST(tenure AS INTEGER) AS tenure_months,
    CASE WHEN PhoneService = 'Yes' THEN 1 ELSE 0 END AS has_phone_service,
    MultipleLines AS multiple_lines,
    InternetService AS internet_service,
    Contract AS contract_type,
    CASE WHEN PaperlessBilling = 'Yes' THEN 1 ELSE 0 END AS is_paperless_billing,
    PaymentMethod AS payment_method,
    
    -- Numerical charge casting & null/whitespace sanitation
    CAST(MonthlyCharges AS DECIMAL(10, 2)) AS monthly_charges,
    CASE 
        WHEN TRIM(TotalCharges) = '' OR TotalCharges IS NULL THEN 0.0
        ELSE CAST(TotalCharges AS DECIMAL(10, 2))
    END AS total_charges,
    
    -- Churn targets
    Churn AS churn_label,
    CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END AS is_churned

FROM raw_telco_churn;
