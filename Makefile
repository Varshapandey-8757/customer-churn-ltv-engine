# Customer Churn Prediction & LTV Engine
# Makefile for quick testing, execution, and verification

PYTHON := python

.PHONY: help test run-sql export-features check-env clean

help:
	@echo "Available commands:"
	@echo "  make test             - Run unit tests on feature pipeline"
	@echo "  make run-sql          - Run SQL pipeline and display business analytics"
	@echo "  make export-features  - Run feature engineering and export model-ready datasets"
	@echo "  make check-env        - Verify Python environment and dependencies"
	@echo "  make clean            - Remove cache and temporary files"

test:
	$(PYTHON) tests/test_feature_engineering.py

run-sql:
	$(PYTHON) scripts/run_sql_pipeline.py

export-features:
	$(PYTHON) scripts/export_model_features.py

check-env:
	$(PYTHON) scripts/verify_environment.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
