import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "db" / "nifty100.db"


def safe_divide(numerator, denominator):
    """Safely divide two values."""
    if numerator is None or denominator in (None, 0):
        return None

    return numerator / denominator


def calculate_ratios(db_path=DB_PATH):
    """
    Calculate financial ratios from aggregated Profit & Loss,
    Balance Sheet and Cash Flow data.

    Source tables are aggregated by company_id + year first
    to prevent duplicate JOIN results.
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT
        p.company_id,
        p.year,

        p.sales,
        p.operating_profit,
        p.net_profit,
        p.interest,
        p.eps,
        p.dividend_payout,

        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.total_assets,

        c.operating_activity,
        c.investing_activity

    FROM
    (
        SELECT
            company_id,
            year,
            SUM(sales) AS sales,
            SUM(operating_profit) AS operating_profit,
            SUM(net_profit) AS net_profit,
            SUM(interest) AS interest,
            AVG(eps) AS eps,
            AVG(dividend_payout) AS dividend_payout
        FROM profitandloss
        GROUP BY company_id, year
    ) p

    LEFT JOIN
    (
        SELECT
            company_id,
            year,
            SUM(equity_capital) AS equity_capital,
            SUM(reserves) AS reserves,
            SUM(borrowings) AS borrowings,
            SUM(total_assets) AS total_assets
        FROM balancesheet
        GROUP BY company_id, year
    ) b
        ON p.company_id = b.company_id
        AND p.year = b.year

    LEFT JOIN
    (
        SELECT
            company_id,
            year,
            SUM(operating_activity) AS operating_activity,
            SUM(investing_activity) AS investing_activity
        FROM cashflow
        GROUP BY company_id, year
    ) c
        ON p.company_id = c.company_id
        AND p.year = c.year

    ORDER BY p.company_id, p.year
    """

    rows = cursor.execute(query).fetchall()

    calculated = []

    for row in rows:

        (
            company_id,
            year,
            sales,
            operating_profit,
            net_profit,
            interest,
            eps,
            dividend_payout,
            equity_capital,
            reserves,
            borrowings,
            total_assets,
            operating_activity,
            investing_activity,
        ) = row

        # -------------------------------------------------
        # Shareholders' Equity
        # -------------------------------------------------

        equity = None

        if equity_capital is not None or reserves is not None:
            equity = (equity_capital or 0) + (reserves or 0)

        # -------------------------------------------------
        # 1. Net Profit Margin
        # -------------------------------------------------

        net_profit_margin = safe_divide(
            net_profit,
            sales
        )

        if net_profit_margin is not None:
            net_profit_margin *= 100

        # -------------------------------------------------
        # 2. Operating Profit Margin
        # -------------------------------------------------

        operating_profit_margin = safe_divide(
            operating_profit,
            sales
        )

        if operating_profit_margin is not None:
            operating_profit_margin *= 100

        # -------------------------------------------------
        # 3. Return on Equity
        # -------------------------------------------------

        roe = safe_divide(
            net_profit,
            equity
        )

        if roe is not None:
            roe *= 100

        # -------------------------------------------------
        # 4. Debt to Equity
        # -------------------------------------------------

        debt_to_equity = safe_divide(
            borrowings,
            equity
        )

        # -------------------------------------------------
        # 5. Interest Coverage
        # -------------------------------------------------

        interest_coverage = safe_divide(
            operating_profit,
            interest
        )

        # -------------------------------------------------
        # 6. Asset Turnover
        # -------------------------------------------------

        asset_turnover = safe_divide(
            sales,
            total_assets
        )

        # -------------------------------------------------
        # 7. Cash From Operations
        # -------------------------------------------------

        cash_from_operations = operating_activity

        # -------------------------------------------------
        # 8. CAPEX Proxy
        #
        # Investing cash flow is used as a proxy because
        # the current database does not contain a dedicated
        # capital-expenditure field.
        # -------------------------------------------------

        capex = None

        if investing_activity is not None:
            capex = abs(investing_activity)

        # -------------------------------------------------
        # 9. Free Cash Flow
        # -------------------------------------------------

        free_cash_flow = None

        if cash_from_operations is not None and capex is not None:
            free_cash_flow = cash_from_operations - capex

        # -------------------------------------------------
        # 10. Dividend Payout
        # -------------------------------------------------

        dividend_payout_ratio = dividend_payout

        # -------------------------------------------------
        # Store result
        # -------------------------------------------------

        calculated.append(
            (
                company_id,
                year,
                net_profit_margin,
                operating_profit_margin,
                roe,
                debt_to_equity,
                interest_coverage,
                asset_turnover,
                free_cash_flow,
                capex,
                eps,
                None,  # Book Value Per Share
                dividend_payout_ratio,
                borrowings,
                cash_from_operations,
            )
        )

    # -----------------------------------------------------
    # Refresh financial_ratios
    # -----------------------------------------------------

    cursor.execute("DELETE FROM financial_ratios")

    cursor.executemany(
        """
        INSERT INTO financial_ratios (
            company_id,
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            capex_cr,
            earnings_per_share,
            book_value_per_share,
            dividend_payout_ratio_pct,
            total_debt_cr,
            cash_from_operations_cr
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        calculated,
    )

    conn.commit()

    count = cursor.execute(
        "SELECT COUNT(*) FROM financial_ratios"
    ).fetchone()[0]

    conn.close()

    return count


if __name__ == "__main__":

    print("=" * 60)
    print("FINANCIAL RATIO ENGINE")
    print("=" * 60)

    count = calculate_ratios()

    print(f"Database: {DB_PATH}")
    print(f"Rows processed: {count}")
    print("Ratio calculation completed successfully.")