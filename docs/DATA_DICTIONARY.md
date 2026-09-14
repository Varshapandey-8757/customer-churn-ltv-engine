# Data Dictionary: Customer Churn & LTV Feature Store

**Project**: Customer Churn Prediction & LTV Engine  
**Owner**: Abhishek (SQL & Feature Engineering)  
**Total Features**: 92 Model-Ready Features + Domain Raw Attributes

---

## 1. Raw Ingestion Attributes

| Column Name | Type | Description | Source / Values |
| :--- | :--- | :--- | :--- |
| `customerID` | String | Unique customer identifier | e.g., `7590-VHVEG` |
| `gender` | String | Customer gender | `Female`, `Male` |
| `SeniorCitizen` | Integer | Whether customer is a senior citizen | `0`, `1` |
| `Partner` | String | Whether customer has a partner | `Yes`, `No` |
| `Dependents` | String | Whether customer has dependents | `Yes`, `No` |
| `tenure` | Integer | Number of months customer has stayed with company | `0` to `72` |
| `PhoneService` | String | Whether customer has phone service | `Yes`, `No` |
| `MultipleLines` | String | Whether customer has multiple lines | `Yes`, `No`, `No phone service` |
| `InternetService` | String | Customer's internet service provider | `DSL`, `Fiber optic`, `No` |
| `OnlineSecurity` | String | Whether customer has online security add-on | `Yes`, `No`, `No internet service` |
| `OnlineBackup` | String | Whether customer has online backup add-on | `Yes`, `No`, `No internet service` |
| `DeviceProtection` | String | Whether customer has device protection add-on | `Yes`, `No`, `No internet service` |
| `TechSupport` | String | Whether customer has tech support add-on | `Yes`, `No`, `No internet service` |
| `StreamingTV` | String | Whether customer streams TV | `Yes`, `No`, `No internet service` |
| `StreamingMovies`| String | Whether customer streams movies | `Yes`, `No`, `No internet service` |
| `Contract` | String | Contract commitment terms | `Month-to-month`, `One year`, `Two year` |
| `PaperlessBilling` | String | Whether customer uses paperless billing | `Yes`, `No` |
| `PaymentMethod` | String | Payment method | `Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)` |
| `MonthlyCharges` | Float | Amount charged to customer monthly | `$18.25` to `$118.75` |
| `TotalCharges` | Float | Total amount charged to customer | Sanitized from string; `$0.00` to `$8684.80` |
| `Churn` | String | Whether customer churned | `Yes`, `No` |

---

## 2. Engineered Feature Families

### A. Tenure & Lifecycle Features
- **`tenure_months`** (Int): Direct tenure in months.
- **`tenure_years`** (Float): `tenure / 12.0`.
- **`log_tenure`** (Float): `log(tenure + 1)`. Non-linear scaling addressing early-tenure churn steepness.
- **`is_new_customer`** (Binary): Flag indicating $tenure \le 6$ months (highest hazard window).
- **`tenure_cohort`** (Categorical): 
  - `0-6m [New]`: Highest risk cohort (hazard peak).
  - `7-12m [Adopter]`: Early adoption phase.
  - `13-24m [Established]`: Mid-lifecycle customer.
  - `25-48m [Mature]`: Low-risk loyal base.
  - `49+m [Veteran]`: Sticky, long-term brand advocate.

### B. Financial & Charges Features
- **`expected_cumulative_charges`** (Float): `tenure * MonthlyCharges`.
- **`charges_ratio`** (Float): `TotalCharges / expected_cumulative_charges`. Highlights promotional discounting, fee hikes, or plan upgrades.
- **`avg_historical_monthly_charge`** (Float): `TotalCharges / (tenure + 1)`.
- **`charge_velocity`** (Float): `MonthlyCharges - avg_historical_monthly_charge`. Positive indicates recent price hike or added service tier.
- **`monthly_charge_tier`** (Categorical): `Low (<$35)`, `Medium ($35-$70)`, `High ($70-$90)`, `Premium (>$90)`.

### C. Contract & Payment Friction
- **`contract_term_months`** (Int): 1 (Month-to-month), 12 (One year), 24 (Two year).
- **`is_month_to_month`** (Binary): Strongest individual predictor of churn risk.
- **`is_autopay_enabled`** (Binary): 1 if automatic bank transfer or credit card; 0 for manual checks.
- **`has_paperless_manual_payment_risk`** (Binary): Interaction of `PaperlessBilling == 1` and `is_autopay == 0`.

### D. Service Usage & Bundling
- **`total_services_count`** (Int): Integer sum of active add-on services (0 to 8).
- **`service_breadth_score`** (Float): Normalized service count (`total_services_count / 8.0`).
- **`is_single_play`** (Binary): Customer with $\le 1$ active service.
- **`has_streaming_bundle`** (Binary): Subscribed to both Streaming TV and Movies.
- **`has_security_bundle`** (Binary): Subscribed to both Online Security and Tech Support.
- **`has_fiber_no_techsupport_risk`** (Binary): High-bandwidth Fiber Optic subscriber without Tech Support. Critical churn vector (**49.37%** churn rate).

### E. Customer Segmentation & LTV Proxies
- **`value_tier`** (Categorical): `High Value` ($\ge \$80/mo$), `Medium Value` ($\$40-\$80/mo$), `Low Value` ($< \$40/mo$).
- **`risk_profile`** (Categorical): `High Risk`, `Moderate Risk`, `Low Risk`.
- **`customer_strategic_segment`** (Categorical): 
  - `High Value - Urgent Retention`
  - `High Value - Loyal VIP`
  - `Low Value - Price Sensitive`
  - `Core Mid-Market`
- **`historical_ltv`** (Float): `TotalCharges`.
- **`estimated_remaining_months`** (Int): Heuristic lifetime projection.
- **`estimated_total_ltv`** (Float): `TotalCharges + (MonthlyCharges * remaining_months)`.
