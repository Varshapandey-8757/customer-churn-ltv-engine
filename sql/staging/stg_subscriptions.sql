-- =============================================================================
-- SQL Staging: stg_subscriptions.sql
-- Project: Customer Churn Prediction & LTV Engine
-- Owner: Abhishek (SQL & Feature Engineering)
-- Description:
--   Normalizes customer subscription lines, internet tier, phone lines, 
--   value-added services (VAS), contract terms, and auto-pay indicators.
-- =============================================================================

SELECT
    customerID AS customer_id,
    
    -- Telephony & Connectivity
    CASE WHEN PhoneService = 'Yes' THEN 1 ELSE 0 END AS has_phone_service,
    CASE WHEN MultipleLines = 'Yes' THEN 1 ELSE 0 END AS has_multiple_lines,
    CASE WHEN InternetService != 'No' THEN 1 ELSE 0 END AS has_internet_service,
    InternetService AS internet_service_type,
    
    -- Value Added Add-on Services (0 if No or No internet service)
    CASE WHEN OnlineSecurity = 'Yes' THEN 1 ELSE 0 END AS has_online_security,
    CASE WHEN OnlineBackup = 'Yes' THEN 1 ELSE 0 END AS has_online_backup,
    CASE WHEN DeviceProtection = 'Yes' THEN 1 ELSE 0 END AS has_device_protection,
    CASE WHEN TechSupport = 'Yes' THEN 1 ELSE 0 END AS has_tech_support,
    CASE WHEN StreamingTV = 'Yes' THEN 1 ELSE 0 END AS has_streaming_tv,
    CASE WHEN StreamingMovies = 'Yes' THEN 1 ELSE 0 END AS has_streaming_movies,
    
    -- Contract Commitment Normalization
    Contract AS contract_type,
    CASE 
        WHEN Contract = 'Month-to-month' THEN 1
        WHEN Contract = 'One year' THEN 12
        WHEN Contract = 'Two year' THEN 24
        ELSE 1
    END AS contract_term_months,
    
    -- Payment & Invoicing
    PaymentMethod AS payment_method,
    CASE 
        WHEN LOWER(PaymentMethod) LIKE '%automatic%' THEN 1 
        ELSE 0 
    END AS is_autopay_enabled,
    CASE WHEN PaperlessBilling = 'Yes' THEN 1 ELSE 0 END AS is_paperless_billing

FROM raw_telco_churn;
