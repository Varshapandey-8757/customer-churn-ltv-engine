# Business Metrics & Retention KPI Report

**Project**: Customer Churn Prediction & LTV Engine  
**Author**: Abhishek (SQL & Feature Engineering)

All numbers below are computed from `fct_churn_ltv_features.csv` (7,043 customer accounts)
and can be reproduced with `make run-sql`.

---

## 1. Topline Business Health Metrics

| Metric                           | Value              | Interpretation                                       |
| :------------------------------- | :----------------- | :--------------------------------------------------- |
| **Total Customer Base**          | 7,043              | Full audited account universe                        |
| **Active Customers**             | 5,174 (73.46%)     | Current retained subscriber pool                     |
| **Churned Customers**            | 1,869 (26.54%)     | Historical lost subscribers                          |
| **Active MRR**                   | $316,985.75 / mo   | Monthly recurring revenue from active customers only |
| **Estimated ARR**                | $3,803,829.00 / yr | Active MRR x 12                                      |
| **Active ARPU**                  | $61.27 / mo        | Average monthly charge of active customers           |
| **Global ARPU**                  | $64.76 / mo        | Average monthly charge across all 7,043 accounts     |
| **Lost Monthly Revenue**         | $139,130.85 / mo   | Monthly charges of churned customers                 |
| **Active MRR at Immediate Risk** | $109,719.90 / mo   | Active customers with a High Risk profile            |

> Note: $456,116.60 is the monthly charge summed over **all** accounts including churned
> ones (Active MRR $316,985.75 + Lost MRR $139,130.85). It is not a current run-rate.

---

## 2. Retention Levers & Churn Catalysts

1. **Fiber Optic Support Gap**:
    - Fiber Optic without Tech Support (2,230 customers) churns at **49.37%**.
    - All other customers (4,813) churn at **15.96%**; customers with Tech Support churn at **15.17%**.
2. **Payment Friction**:
    - Paperless billing paired with Electronic Check (1,742 customers) churns at **49.77%**.
    - Customers on Auto-Pay (3,066) churn at **15.98%**.
3. **Contract Horizon**:
    - Month-to-month contracts (3,875) churn at **42.71%**.
    - 1-Year contracts (1,473) churn at **11.27%**.
    - 2-Year contracts (1,695) churn at **2.83%**.
