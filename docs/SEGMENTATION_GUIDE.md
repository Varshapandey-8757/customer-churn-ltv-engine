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

The four segments are assigned in this order (first match wins), and together cover all 7,043 accounts.

### Segment 1: High Value - Urgent Retention

- **Criteria**: `MonthlyCharges >= $80.0` AND (`is_month_to_month == 1` OR `has_fiber_no_techsupport_risk == 1`).
- **Volume**: 1,885 accounts (1,051 active).
- **Churn Rate**: **44.24%** (54.81% for the 1,350 accounts that also have a High Risk profile).
- **ARPU**: $94.00 / month. **Avg Historical LTV**: $3,133.00.
- **MRR at Stake**: **$99,350.25 / month** (active accounts only).
- **Action Playbook**:
    - Assign to VIP customer success specialists within 24 hours.
    - Offer a discounted 1-year contract lock-in with complimentary Tech Support and security add-ons.

### Segment 2: High Value - Loyal VIP

- **Criteria**: `MonthlyCharges >= $80.0` and not in Segment 1 (so: not month-to-month and no Fiber-without-Tech-Support gap).
- **Volume**: 792 accounts (716 active).
- **Churn Rate**: **9.60%**.
- **Avg Historical LTV**: **$5,980.27**. **Active MRR**: $70,261.25.
- **Action Playbook**:
    - Priority loyalty tier, early access to new streaming features, zero-rate device upgrades.

### Segment 3: Low Value - Price Sensitive

- **Criteria**: `MonthlyCharges < $40.0` on Month-to-Month contracts.
- **Volume**: 761 accounts (565 active).
- **Churn Rate**: **25.76%**.
- **ARPU**: $23.57 / month.
- **Action Playbook**:
    - Automated self-service nudges, bundle promotions with low incremental cost.

### Segment 4: Core Mid-Market

- **Criteria**: Everything else: $40 - $80 per month on any contract, plus accounts under $40 on 1-2 year contracts.
- **Volume**: 3,605 accounts (2,842 active).
- **Churn Rate**: **21.17%**.
- **ARPU**: $50.73 / month. **Active MRR**: $134,383.50.
- **Action Playbook**:
    - Service expansion campaigns: promote Online Security & Tech Support to increase stickiness.
