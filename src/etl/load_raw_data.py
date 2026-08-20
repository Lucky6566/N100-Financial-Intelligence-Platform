from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_raw_data():
    """Load raw company and financial data."""

    companies_path = RAW_DATA_DIR / "companies.csv"
    financials_path = RAW_DATA_DIR / "financials.csv"

    companies = pd.read_csv(companies_path)
    financials = pd.read_csv(financials_path)

    print("Companies data loaded:")
    print(f"Rows: {len(companies)}")
    print(f"Columns: {len(companies.columns)}")

    print("\nFinancial data loaded:")
    print(f"Rows: {len(financials)}")
    print(f"Columns: {len(financials.columns)}")

    return companies, financials


def save_processed_data(companies, financials):
    """Save cleaned copies to the processed directory."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    companies.to_csv(
        PROCESSED_DATA_DIR / "companies.csv",
        index=False
    )

    financials.to_csv(
        PROCESSED_DATA_DIR / "financials.csv",
        index=False
    )

    print("\nProcessed files saved successfully.")


if __name__ == "__main__":
    companies, financials = load_raw_data()
    save_processed_data(companies, financials)