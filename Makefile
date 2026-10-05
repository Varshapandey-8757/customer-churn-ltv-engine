PYTHON := python

.PHONY: help test export-features train api run-sql check-env clean

help:
	@echo "Available commands:"
	@echo "  make export-features  - Run feature engineering and export model-ready datasets"
	@echo "  make train            - Train churn + LTV models (needs export-features first)"
	@echo "  make test             - Run the full test suite"
	@echo "  make api              - Start the prediction API on http://127.0.0.1:8000/docs"
	@echo "  make run-sql          - Run SQL pipeline and display business analytics"
	@echo "  make check-env        - Verify Python environment and dependencies"
	@echo "  make clean            - Remove cache and temporary files"

export-features:
	$(PYTHON) scripts/export_model_features.py

train:
	$(PYTHON) -m src.models.train_churn
	$(PYTHON) -m src.models.train_ltv

test:
	$(PYTHON) -m pytest tests -q

api:
	$(PYTHON) -m uvicorn api.main:app --reload

run-sql:
	$(PYTHON) scripts/run_sql_pipeline.py

check-env:
	$(PYTHON) scripts/verify_environment.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
