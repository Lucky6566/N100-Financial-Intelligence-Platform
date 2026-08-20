from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

def load_data():
    """Load processed company and financial data."""

    companies = pd.read_csv(
        PROCESSED_DATA_DIR / "companies.csv"
    )

    financials = pd.read_csv(
        PROCESSED_DATA_DIR / "financials.csv"
    )

    return companies, financials


# ---------------------------------------------------------
# Calculate financial KPIs
# ---------------------------------------------------------

def calculate_kpis(companies, financials):
    """Calculate financial KPIs for each company and year."""

    df = financials.merge(
        companies[
            [
                "company_id",
                "company_name",
                "ticker",
                "sector",
                "industry",
            ]
        ],
        on="company_id",
        how="left",
    )

    # Sort data for year-over-year calculations
    df = df.sort_values(
        ["company_id", "year"]
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # Profitability KPIs
    # -----------------------------------------------------

    df["profit_margin_pct"] = (
        df["net_income"] / df["revenue"] * 100
    )

    df["roa_pct"] = (
        df["net_income"] / df["total_assets"] * 100
    )

    # -----------------------------------------------------
    # Leverage KPI
    # -----------------------------------------------------

    df["debt_to_asset_pct"] = (
        df["total_liabilities"]
        / df["total_assets"]
        * 100
    )

    # -----------------------------------------------------
    # Cash flow KPI
    # -----------------------------------------------------

    df["cash_flow_margin_pct"] = (
        df["cash_flow"] / df["revenue"] * 100
    )

    # -----------------------------------------------------
    # Year-over-year growth KPIs
    # -----------------------------------------------------

    df["revenue_growth_pct"] = (
        df.groupby("company_id")["revenue"]
        .pct_change()
        * 100
    )

    df["net_income_growth_pct"] = (
        df.groupby("company_id")["net_income"]
        .pct_change()
        * 100
    )

    df["eps_growth_pct"] = (
        df.groupby("company_id")["eps"]
        .pct_change()
        * 100
    )

    # -----------------------------------------------------
    # Round KPI values
    # -----------------------------------------------------

    kpi_columns = [
        "profit_margin_pct",
        "roa_pct",
        "debt_to_asset_pct",
        "cash_flow_margin_pct",
        "revenue_growth_pct",
        "net_income_growth_pct",
        "eps_growth_pct",
    ]

    df[kpi_columns] = df[kpi_columns].round(2)

    return df


# ---------------------------------------------------------
# Save KPI output
# ---------------------------------------------------------

def save_kpis(kpi_data):
    """Save calculated KPIs to the output directory."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = OUTPUT_DIR / "financial_kpis.csv"

    kpi_data.to_csv(
        output_path,
        index=False
    )

    print(f"\nKPI output saved to:")
    print(output_path)

    return output_path


# ---------------------------------------------------------
# Main execution
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Loading financial data...")

    companies, financials = load_data()

    print(
        f"Companies loaded: {len(companies)}"
    )

    print(
        f"Financial records loaded: {len(financials)}"
    )

    print("\nCalculating financial KPIs...")

    kpi_data = calculate_kpis(
        companies,
        financials
    )

    print(
        f"KPI records generated: {len(kpi_data)}"
    )

    save_kpis(kpi_data)

    print("\nFinancial KPI calculation completed successfully.")

    print("\nSample KPI results:")

    print(
        kpi_data[
            [
                "company_name",
                "year",
                "revenue_growth_pct",
                "profit_margin_pct",
                "roa_pct",
                "debt_to_asset_pct",
                "eps_growth_pct",
            ]
        ].head(10).to_string(index=False)
    )