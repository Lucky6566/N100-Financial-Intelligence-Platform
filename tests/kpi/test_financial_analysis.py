import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "output"

RANKING_FILE = OUTPUT_DIR / "company_performance_ranking.csv"
SCORE_FILE = OUTPUT_DIR / "company_financial_scores.csv"


def test_ranking_file_exists():
    assert RANKING_FILE.exists()


def test_score_file_exists():
    assert SCORE_FILE.exists()


def test_ranking_has_all_companies():
    df = pd.read_csv(RANKING_FILE)

    assert len(df) == 10
    assert df["company_name"].nunique() == 10


def test_scores_have_all_companies():
    df = pd.read_csv(SCORE_FILE)

    assert len(df) == 10
    assert df["company_name"].nunique() == 10


def test_financial_scores_are_valid():
    df = pd.read_csv(SCORE_FILE)

    assert df["financial_score"].notna().all()
    assert (df["financial_score"] >= 0).all()
    assert (df["financial_score"] <= 100).all()


def test_financial_ranks_are_unique():
    df = pd.read_csv(RANKING_FILE)

    ranks = df["financial_rank"]

    assert ranks.nunique() == 10
    assert set(ranks) == set(range(1, 11))


def test_ranking_is_sorted():
    df = pd.read_csv(RANKING_FILE)

    scores = df["financial_score"].tolist()

    assert scores == sorted(scores, reverse=True)


def test_required_score_columns_exist():
    df = pd.read_csv(SCORE_FILE)

    required_columns = [
        "company_name",
        "financial_score",
        "financial_rank",
        "growth_score",
        "profitability_score",
        "roa_score",
        "leverage_score",
        "eps_score",
    ]

    for column in required_columns:
        assert column in df.columns


def test_component_scores_are_valid():
    df = pd.read_csv(SCORE_FILE)

    score_columns = [
        "growth_score",
        "profitability_score",
        "roa_score",
        "leverage_score",
        "eps_score",
    ]

    for column in score_columns:
        assert df[column].notna().all()
        assert (df[column] >= 0).all()
        assert (df[column] <= 100).all()
        