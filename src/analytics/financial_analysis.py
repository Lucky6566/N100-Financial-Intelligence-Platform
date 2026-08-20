import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "output" / "financial_kpis.csv"
OUTPUT_DIR = BASE_DIR / "output"

RANKING_FILE = OUTPUT_DIR / "company_performance_ranking.csv"
SCORE_FILE = OUTPUT_DIR / "company_financial_scores.csv"


def load_kpis():
    """Load calculated financial KPIs."""
    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Financial KPI file is empty.")

    return df


def calculate_company_metrics(df):
    """
    Calculate company-level financial intelligence metrics.
    """

    # Average performance across available years
    metrics = (
        df.groupby("company_name")
        .agg(
            avg_revenue_growth_pct=("revenue_growth_pct", "mean"),
            avg_profit_margin_pct=("profit_margin_pct", "mean"),
            avg_roa_pct=("roa_pct", "mean"),
            avg_debt_to_asset_pct=("debt_to_asset_pct", "mean"),
            avg_eps_growth_pct=("eps_growth_pct", "mean"),
        )
        .reset_index()
    )

    # Replace missing growth values with zero for scoring
    growth_columns = [
        "avg_revenue_growth_pct",
        "avg_eps_growth_pct",
    ]

    for column in growth_columns:
        metrics[column] = metrics[column].fillna(0)

    return metrics


def create_rankings(metrics):
    """Create individual KPI rankings."""

    metrics["revenue_growth_rank"] = (
        metrics["avg_revenue_growth_pct"]
        .rank(ascending=False, method="min")
    )

    metrics["profitability_rank"] = (
        metrics["avg_profit_margin_pct"]
        .rank(ascending=False, method="min")
    )

    metrics["roa_rank"] = (
        metrics["avg_roa_pct"]
        .rank(ascending=False, method="min")
    )

    # Lower debt is better
    metrics["leverage_rank"] = (
        metrics["avg_debt_to_asset_pct"]
        .rank(ascending=True, method="min")
    )

    metrics["eps_growth_rank"] = (
        metrics["avg_eps_growth_pct"]
        .rank(ascending=False, method="min")
    )

    return metrics


def calculate_financial_score(metrics):
    """
    Calculate a composite financial intelligence score.

    Weights:
    Revenue Growth      = 20%
    Profit Margin       = 25%
    ROA                 = 20%
    Debt-to-Asset       = 15%
    EPS Growth          = 20%
    """

    def normalize(series, higher_is_better=True):
        min_value = series.min()
        max_value = series.max()

        if max_value == min_value:
            return pd.Series(50.0, index=series.index)

        score = (
            (series - min_value)
            / (max_value - min_value)
            * 100
        )

        if not higher_is_better:
            score = 100 - score

        return score

    metrics["growth_score"] = normalize(
        metrics["avg_revenue_growth_pct"],
        higher_is_better=True
    )

    metrics["profitability_score"] = normalize(
        metrics["avg_profit_margin_pct"],
        higher_is_better=True
    )

    metrics["roa_score"] = normalize(
        metrics["avg_roa_pct"],
        higher_is_better=True
    )

    metrics["leverage_score"] = normalize(
        metrics["avg_debt_to_asset_pct"],
        higher_is_better=False
    )

    metrics["eps_score"] = normalize(
        metrics["avg_eps_growth_pct"],
        higher_is_better=True
    )

    metrics["financial_score"] = (
        metrics["growth_score"] * 0.20
        + metrics["profitability_score"] * 0.25
        + metrics["roa_score"] * 0.20
        + metrics["leverage_score"] * 0.15
        + metrics["eps_score"] * 0.20
    )

    metrics["financial_rank"] = (
        metrics["financial_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    return metrics


def main():

    print("Loading financial KPI data...")

    df = load_kpis()

    print(f"Records loaded: {len(df)}")

    metrics = calculate_company_metrics(df)

    metrics = create_rankings(metrics)

    metrics = calculate_financial_score(metrics)

    # Sort by overall financial score
    ranking = metrics.sort_values(
        "financial_score",
        ascending=False
    ).reset_index(drop=True)

    ranking.to_csv(
        RANKING_FILE,
        index=False
    )

    score_columns = [
        "company_name",
        "financial_score",
        "financial_rank",
        "growth_score",
        "profitability_score",
        "roa_score",
        "leverage_score",
        "eps_score",
    ]

    scores = ranking[score_columns]

    scores.to_csv(
        SCORE_FILE,
        index=False
    )

    print()
    print("Financial intelligence analysis completed successfully.")
    print()
    print("Top companies:")
    print(
        ranking[
            [
                "financial_rank",
                "company_name",
                "financial_score",
                "avg_revenue_growth_pct",
                "avg_profit_margin_pct",
                "avg_roa_pct",
                "avg_debt_to_asset_pct",
            ]
        ].head(10).to_string(index=False)
    )

    print()
    print(f"Ranking saved to: {RANKING_FILE}")
    print(f"Scores saved to: {SCORE_FILE}")


if __name__ == "__main__":
    main()