# Customer Strategic Segmentation Guide

**Project**: Customer Churn Prediction & LTV Engine  
**Author**: Abhishek (SQL & Feature Engineering)

---

## 1. Executive Summary

Traditional churn models only predict the likelihood that a customer leaves ($P(\text{churn})$). However, customer success and marketing teams need an actionable, value-weighted retention strategy. 

Our segmentation engine implements a **2x2 Value-to-Risk Matrix** combining Monetary Worth (`MonthlyCharges` & `TotalCharges`) with Churn Exposure (`Contract`, `Tenure`, `PaymentMethod`, and `Support Attach`).

```
                    High Risk                 Low Risk
               +-------------------------+-------------------------+
               |  URGENT RETENTION       |  LOYAL VIPs             |
  High Value   |  (Priority 1: Concierge |  (Priority 3: Upsell,   |
  (MRR >= $80) |   outreach, discounts)  |   loyalty rewards)      |
               +-------------------------+-------------------------+
               |  PRICE SENSITIVE        |  CORE BASE              |
  Low Value    |  (Priority 2: Automated |  (Priority 4: Baseline  |
  (MRR < $40)  |   email/SMS nurture)    |   cross-sell add-ons)   |
               +-------------------------+-------------------------+
```

---

## 2. Segment Deep Dive & Action Playbooks

### Segment 1: High Value - Urgent Retention
- **Criteria**: `MonthlyCharges >= $80.0` AND (`is_month_to_month == 1` OR `has_fiber_no_techsupport_risk == 1`).
- **Volume**: 1,350 accounts (1,051 active).
- **Churn Rate**: **54.81%** (highest revenue loss vector).
- **MRR at Stake**: **$99,350.25 / month**.
- **Action Playbook**:
  - Assign to VIP customer success specialists within 24 hours.
  - Offer a discounted 1-year contract lock-in with complimentary Tech Support and security add-ons.

### Segment 2: High Value - Loyal VIP
- **Criteria**: `MonthlyCharges >= $80.0` with 1-2 Year contract and auto-pay enabled.
- **Volume**: 762 accounts.
- **Churn Rate**: **9.45%**.
- **Avg Historical LTV**: **$6,126.17**.
- **Action Playbook**:
  - Priority loyalty tier, early access to new streaming features, zero-rate device upgrades.

### Segment 3: Low Value - Price Sensitive
- **Criteria**: `MonthlyCharges < $40.0` on Month-to-Month contracts.
- **Volume**: 1,180 accounts.
- **Churn Rate**: **38.20%**.
- **Action Playbook**:
  - Automated self-service nudges, bundle promotions with low incremental cost.

### Segment 4: Core Mid-Market
- **Criteria**: Standard single/double play subscribers ($40 - $80/mo).
- **Action Playbook**:
  - Service expansion campaigns: promote Online Security & Tech Support to increase stickiness.
