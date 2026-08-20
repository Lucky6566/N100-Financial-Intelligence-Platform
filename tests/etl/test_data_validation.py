from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def test_companies_file_exists():
    path = PROCESSED_DIR / "companies.csv"
    assert path.exists(), "companies.csv does not exist"


def test_financials_file_exists():
    path = PROCESSED_DIR / "financials.csv"
    assert path.exists(), "financials.csv does not exist"


def test_companies_schema():
    path = PROCESSED_DIR / "companies.csv"
    df = pd.read_csv(path)

    expected_columns = [
        "company_id",
        "company_name",
        "ticker",
        "sector",
        "industry",
    ]

    assert list(df.columns) == expected_columns
def test_financials_schema():
    path = PROCESSED_DIR / "financials.csv"
    df = pd.read_csv(path)

    expected_columns = [
        "company_id",
        "year",
        "revenue",
        "net_income",
        "total_assets",
        "total_liabilities",
        "cash_flow",
        "eps",
    ]

    assert list(df.columns) == expected_columns


def test_company_ids_are_unique():
    path = PROCESSED_DIR / "companies.csv"
    df = pd.read_csv(path)

    assert df["company_id"].is_unique


def test_financials_have_valid_years():
    path = PROCESSED_DIR / "financials.csv"
    df = pd.read_csv(path)

    assert df["year"].between(2023, 2025).all()


def test_financials_have_no_missing_values():
    path = PROCESSED_DIR / "financials.csv"
    df = pd.read_csv(path)

    assert not df.isnull().any().any()


def test_financials_company_ids_exist():
    companies = pd.read_csv(PROCESSED_DIR / "companies.csv")
    financials = pd.read_csv(PROCESSED_DIR / "financials.csv")

    valid_ids = set(companies["company_id"])

    assert set(financials["company_id"]).issubset(valid_ids)