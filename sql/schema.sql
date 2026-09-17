-- Customer Churn LTV Engine
-- PostgreSQL Database Schema

-- Create staging schema
CREATE SCHEMA IF NOT EXISTS staging;

-- Raw Telco Customer Churn data
CREATE TABLE IF NOT EXISTS staging.telco_customer_churn (
    customer_id VARCHAR(20) PRIMARY KEY,
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
    total_charges NUMERIC(12,2),
    churn VARCHAR(10)
);

-- Customer churn table
CREATE TABLE IF NOT EXISTS customer_churn (
    customer_id VARCHAR(20) PRIMARY KEY,
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
    total_charges NUMERIC(12,2),
    churn VARCHAR(10)
);
