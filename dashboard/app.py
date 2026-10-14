"""
Churn & LTV dashboard (Streamlit).

Run from the project root:
    pip install streamlit
    python -m src.data.export_postgres_features     # creates the CSV once
    streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data" / "processed" / "postgres_fct_churn_ltv_features.csv"
)
COHORT_ORDER = [
    "0-6m [New]", "7-12m [Adopter]", "13-24m [Established]",
    "25-48m [Mature]", "49+m [Veteran]",
]

st.set_page_config(page_title="Churn & LTV Dashboard", layout="wide")
st.title("Customer Churn & LTV Dashboard")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


if not DATA_FILE.exists():
    st.error(
        "Data file not found. Run: python -m src.data.export_postgres_features"
    )
    st.stop()

df = load_data()

# ---------------------------------------------------------------- filters
st.sidebar.header("Filters")
contracts = st.sidebar.multiselect(
    "Contract", sorted(df["contract_type"].unique()),
    default=sorted(df["contract_type"].unique()),
)
tiers = st.sidebar.multiselect(
    "Value tier", sorted(df["value_tier"].unique()),
    default=sorted(df["value_tier"].unique()),
)
view = df[df["contract_type"].isin(contracts) & df["value_tier"].isin(tiers)]

if view.empty:
    st.warning("No customers match the selected filters.")
    st.stop()

# ---------------------------------------------------------------- KPIs
active = view[view["is_churned"] == 0]
at_risk = active[active["risk_profile"] == "High Risk"]
urgent = active[
    active["customer_strategic_segment"] == "High Value - Urgent Retention"
]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{len(view):,}")
c2.metric("Churn rate", f"{view['is_churned'].mean() * 100:.2f}%")
c3.metric("Active MRR", f"${active['monthly_charges'].sum():,.0f}")
c4.metric("MRR at risk (High Risk)", f"${at_risk['monthly_charges'].sum():,.0f}")
c5.metric("Urgent retention accounts", f"{len(urgent):,}")

st.divider()

# ---------------------------------------------------------------- charts
left, right = st.columns(2)

with left:
    st.subheader("Churn rate by contract (%)")
    by_contract = view.groupby("contract_type")["is_churned"].mean() * 100
    st.bar_chart(by_contract.round(2))

with right:
    st.subheader("Churn rate by tenure cohort (%)")
    by_cohort = (view.groupby("tenure_cohort")["is_churned"].mean() * 100)
    by_cohort = by_cohort.reindex(
        [c for c in COHORT_ORDER if c in by_cohort.index]
    )
    st.bar_chart(by_cohort.round(2))

left, right = st.columns(2)

with left:
    st.subheader("Active MRR at risk by strategic segment ($)")
    risk_by_segment = (
        at_risk.groupby("customer_strategic_segment")["monthly_charges"].sum()
    )
    if risk_by_segment.empty:
        st.info("No high-risk active customers in this selection.")
    else:
        st.bar_chart(risk_by_segment.round(0))

with right:
    st.subheader("Churn rate by service enrolment (%)")
    rows = []
    for label, col in [
        ("Tech Support", "has_tech_support"),
        ("Online Security", "has_online_security"),
        ("Streaming bundle", "has_streaming_bundle"),
    ]:
        grouped = view.groupby(col)["is_churned"].mean() * 100
        rows.append({
            "Service": label,
            "Enrolled": round(float(grouped.get(1, float("nan"))), 2),
            "Not enrolled": round(float(grouped.get(0, float("nan"))), 2),
        })
    st.bar_chart(pd.DataFrame(rows).set_index("Service"))

st.divider()
st.subheader("Highest-risk active customers")
st.dataframe(
    at_risk.sort_values("monthly_charges", ascending=False)[
        ["customer_id", "tenure_months", "contract_type", "payment_method",
         "monthly_charges", "customer_strategic_segment"]
    ].head(50),
    width="stretch", hide_index=True,
)
