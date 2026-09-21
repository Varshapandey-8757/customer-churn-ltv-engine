-- Customer Churn LTV Engine
-- PostgreSQL Database Schema

-- =========================================================
-- 1. Create schemas
-- =========================================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;


-- =========================================================
-- 2. Raw Telco Customer Churn data
-- =========================================================
-- Raw layer keeps all CSV values as TEXT.
-- Type conversions happen in the cleaned staging layer.

CREATE TABLE IF NOT EXISTS staging.telco_customer_churn_raw (
    customer_id TEXT,
    gender TEXT,
    senior_citizen TEXT,
    partner TEXT,
    dependents TEXT,
    tenure TEXT,
    phone_service TEXT,
    multiple_lines TEXT,
    internet_service TEXT,
    online_security TEXT,
    online_backup TEXT,
    device_protection TEXT,
    tech_support TEXT,
    streaming_tv TEXT,
    streaming_movies TEXT,
    contract TEXT,
    paperless_billing TEXT,
    payment_method TEXT,
    monthly_charges TEXT,
    total_charges TEXT,
    churn TEXT
);


-- =========================================================
-- 3. Cleaned staging table
-- =========================================================

CREATE TABLE IF NOT EXISTS staging.telco_customer_churn (
    customer_id VARCHAR(20),
    gender VARCHAR(20),
    senior_citizen INTEGER,
    partner VARCHAR(10),
    dependents VARCHAR(10),
    tenure INTEGER,
    phone_service VARCHAR(30),
    multiple_lines VARCHAR(50),
    internet_service VARCHAR(30),
    online_security VARCHAR(30),
    online_backup VARCHAR(30),
    device_protection VARCHAR(30),
    tech_support VARCHAR(30),
    streaming_tv VARCHAR(30),
    streaming_movies VARCHAR(30),
    contract VARCHAR(50),
    paperless_billing VARCHAR(10),
    payment_method VARCHAR(50),
    monthly_charges NUMERIC(10,2),
    total_charges NUMERIC(10,2),
    churn VARCHAR(10)
);


-- Primary key for cleaned staging table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'telco_customer_churn_pk'
    ) THEN
        ALTER TABLE staging.telco_customer_churn
        ADD CONSTRAINT telco_customer_churn_pk
        PRIMARY KEY (customer_id);
    END IF;
END $$;