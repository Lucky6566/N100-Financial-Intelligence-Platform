from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_kpis():
    """Load the generated KPI dataset."""
    return pd.read_csv(
        OUTPUT_DIR / "financial_kpis.csv"
    )


def test_kpi_file_exists():
    """KPI output file must exist."""

    path = OUTPUT_DIR / "financial_kpis.csv"

    assert path.exists()


def test_kpi_record_count():
    """There should be 30 financial KPI records."""

    df = load_kpis()

    assert len(df) == 30


def test_all_companies_present():
    """All 10 companies should be represented."""

    df = load_kpis()

    assert df["company_id"].nunique() == 10


def test_all_years_present():
    """Financial years 2023, 2024 and 2025 must exist."""

    df = load_kpis()

    assert set(df["year"]) == {2023, 2024, 2025}


def test_profit_margin_is_valid():
    """Profit margin should be calculated correctly."""

    df = load_kpis()

    expected = (
        df["net_income"]
        / df["revenue"]
        * 100
    )

    pd.testing.assert_series_equal(
        df["profit_margin_pct"],
        expected.round(2),
        check_names=False
    )


def test_roa_is_valid():
    """Return on Assets should be calculated correctly."""

    df = load_kpis()

    expected = (
        df["net_income"]
        / df["total_assets"]
        * 100
    )

    pd.testing.assert_series_equal(
        df["roa_pct"],
        expected.round(2),
        check_names=False
    )


def test_debt_to_asset_ratio_is_valid():
    """Debt-to-asset ratio should be calculated correctly."""

    df = load_kpis()

    expected = (
        df["total_liabilities"]
        / df["total_assets"]
        * 100
    )

    pd.testing.assert_series_equal(
        df["debt_to_asset_pct"],
        expected.round(2),
        check_names=False
    )


def test_revenue_growth_has_expected_nulls():
    """First year of each company should have no growth value."""

    df = load_kpis()

    first_year_rows = df[df["year"] == 2023]

    assert first_year_rows["revenue_growth_pct"].isna().all()


def test_growth_values_exist_after_first_year():
    """2024 and 2025 should contain revenue growth values."""

    df = load_kpis()

    later_years = df[df["year"] > 2023]

    assert later_years["revenue_growth_pct"].notna().all()


def test_no_negative_revenue():
    """Revenue cannot be negative."""

    df = load_kpis()

    assert (df["revenue"] >= 0).all()


def test_no_negative_total_assets():
    """Total assets cannot be negative."""

    df = load_kpis()

    assert (df["total_assets"] >= 0).all()