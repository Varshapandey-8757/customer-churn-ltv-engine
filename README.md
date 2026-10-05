# Customer Churn Prediction & LTV Engine

End-to-end analytics project on the Telco customer dataset (7,043 customers, 26.5% churn):
SQL pipeline, feature engineering, churn model, LTV model, SHAP explanations and a prediction API.

## Project structure

```
api/             FastAPI service (churn, LTV, SHAP explain endpoints)
src/data/        Ingestion, cleaning, validation, PostgreSQL loading
src/features/    Feature engineering (93 model features) + CustomerFeatureEngineer
src/models/      Training scripts (train_churn.py, train_ltv.py) and shared utils
src/explainability/  SHAP explainer
sql/             Staging, transformation and analytics queries
notebooks/       Ingestion, feature engineering, churn and LTV notebooks
tests/           Feature, model and API tests
docs/            Data dictionary, KPIs, segmentation and SQL guides
dashboard/       Apache Superset dashboard plan
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

make export-features            # raw CSV -> data/processed/
make train                      # trains churn + LTV models -> models/
make test                       # runs all tests
make api                        # http://127.0.0.1:8000/docs
```

Without `make`: use the commands inside the `Makefile` directly.

## Models

**Churn** - Logistic Regression, Random Forest and XGBoost are compared on the
engineered features; the best ROC-AUC is saved. The decision threshold is
tuned on out-of-fold training predictions, so the test set is used once.
Latest numbers are written to `models/metrics.json` after `make train`.

**LTV** - Random Forest regressor predicting historical customer value
(`TotalCharges`). Columns that contain or are computed from `TotalCharges`
(`TotalCharges`, `expected_cumulative_charges`, `charges_ratio`,
`avg_historical_monthly_charge`, `charge_velocity`, `historical_ltv`,
`estimated_total_ltv`) are removed to prevent target leakage. A guard test
fails if they come back.

Forward-looking value returned by the API:
`projected_ltv = TotalCharges + MonthlyCharges x remaining_months x (1 - churn_probability)`

## API

| Endpoint                    | Purpose                                            |
| :-------------------------- | :------------------------------------------------- |
| `POST /churn/predict`       | Churn probability and risk level for one customer  |
| `POST /churn/predict/batch` | Same, for a list of customers                      |
| `POST /churn/explain`       | Top SHAP factors behind the prediction             |
| `POST /ltv/predict`         | Historical LTV (model) and projected LTV (formula) |
| `GET /health`               | Health check                                       |

Open `/docs` for interactive examples with a sample customer.

## Docker

```bash
make train                      # models must exist before building
docker compose up --build       # API on http://localhost:8000
```

## Business insights

- Month-to-month contracts churn at 42.7%; two-year contracts at 2.8%.
- Fiber Optic customers without Tech Support churn at 49.4%.
- Paperless billing with manual electronic check churns at 57.3%; auto-pay at 15.8%.

See `docs/` for the full KPI report, segmentation playbook and data dictionary.

## Status

- [x] Data ingestion, cleaning, validation
- [x] PostgreSQL schema and SQL pipeline
- [x] Feature engineering with tests
- [x] Churn model and LTV model (leakage fixed)
- [x] Prediction API and SHAP explanations
- [x] Dockerfile
- [ ] Superset dashboard (plan in `dashboard/superset_or_metabase/`)
- [ ] CI pipeline

## Team

Varsha (modeling, API), Abhishek (SQL and feature engineering), and teammates
(data engineering and analytics branches).

## License

See `LICENSE`.
