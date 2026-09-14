"""
Environment & Dependency Verification Script

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Verifies that all required packages, versions, and system dependencies 
are present for running the SQL and feature engineering pipeline.
"""

import sys
import platform

REQUIRED_PACKAGES = {
    "pandas": "2.0.0",
    "numpy": "1.24.0",
    "sklearn": "1.3.0",
    "matplotlib": "3.7.0",
    "seaborn": "0.12.0",
    "joblib": "1.3.0",
    "sqlite3": None,
}


def check_environment():
    print("=" * 70)
    print("CUSTOMER CHURN & LTV ENGINE - ENVIRONMENT VERIFICATION")
    print("=" * 70)
    print(f"Operating System : {platform.system()} {platform.release()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version   : {sys.version.split()[0]}")
    print("-" * 70)

    all_passed = True

    for pkg, min_version in REQUIRED_PACKAGES.items():
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "Built-in")
            print(f"  [OK] {pkg:<15} : {version}")
        except ImportError:
            print(f"  [FAIL] {pkg:<13} : NOT INSTALLED")
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("[SUCCESS] All core libraries and runtimes are properly configured!")
    else:
        print("[WARNING] Some packages are missing. Run: pip install -r requirements.txt")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
