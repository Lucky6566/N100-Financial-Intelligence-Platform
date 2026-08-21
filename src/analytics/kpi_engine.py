import sqlite3
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

DB_PATH = Path(__file__).resolve().parents[2] / "db" / "nifty100.db"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_divide(numerator, denominator):
    """
    Safely divide two numbers.

    Returns None when the denominator is zero or unavailable.
    """
    if numerator is None or denominator in (None, 0):
        return None

    return numerator / denominator


def percentage(numerator, denominator):
    """
    Calculate percentage safely.
    """
    result = safe_divide(numerator, denominator)

    if result is None:
        return None

    return result * 100


def growth(current, previous):
    """
    Calculate year-over-year growth percentage.
    """
    if current is None or previous in (None, 0):
        return None

    return ((current - previous) / abs(previous)) * 100


# ============================================================
# KPI ENGINE
# ============================================================

def calculate_kpis(db_path=DB_PATH):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ========================================================
    # SOURCE DATA
    # Aggregate each source table before joining.
    #
    # This prevents duplicate company/year combinations.
    # ========================================================

    query = """
    SELECT
        p.company_id,
        p.year,

        p.sales,
        p.operating_profit,
        p.net_profit,
        p.interest,
        p.depreciation,
        p.profit_before_tax,
        p.tax_percentage,
        p.eps,
        p.dividend_payout,

        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.total_assets,
        b.fixed_assets,
        b.investments,

        c.operating_activity,
        c.investing_activity,
        c.financing_activity,

        m.market_cap_crore,
        m.enterprise_value_crore,
        m.pe_ratio,
        m.pb_ratio,
        m.ev_ebitda,
        m.dividend_yield_pct

    FROM
    (
        SELECT
            company_id,
            year,
            SUM(sales) AS sales,
            SUM(operating_profit) AS operating_profit,
            SUM(net_profit) AS net_profit,
            SUM(interest) AS interest,
            SUM(depreciation) AS depreciation,
            SUM(profit_before_tax) AS profit_before_tax,
            AVG(tax_percentage) AS tax_percentage,
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
            SUM(total_assets) AS total_assets,
            SUM(fixed_assets) AS fixed_assets,
            SUM(investments) AS investments
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
            SUM(investing_activity) AS investing_activity,
            SUM(financing_activity) AS financing_activity
        FROM cashflow
        GROUP BY company_id, year
    ) c
        ON p.company_id = c.company_id
        AND p.year = c.year

    LEFT JOIN
    (
        SELECT
            company_id,
            year,
            MAX(market_cap_crore) AS market_cap_crore,
            MAX(enterprise_value_crore) AS enterprise_value_crore,
            MAX(pe_ratio) AS pe_ratio,
            MAX(pb_ratio) AS pb_ratio,
            MAX(ev_ebitda) AS ev_ebitda,
            MAX(dividend_yield_pct) AS dividend_yield_pct
        FROM market_cap
        GROUP BY company_id, year
    ) m
        ON p.company_id = m.company_id
        AND CAST(p.year AS TEXT) = CAST(m.year AS TEXT)

    ORDER BY
        p.company_id,
        p.year
    """

    rows = cursor.execute(query).fetchall()

    print(f"Source records found: {len(rows)}")

    # ========================================================
    # HISTORICAL DATA
    # Used for year-over-year growth calculations.
    # ========================================================

    history = {}

    for row in rows:

        company_id = row[0]
        year = row[1]

        history[(company_id, year)] = row

    calculated = []

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    for row in rows:

        (
            company_id,
            year,

            sales,
            operating_profit,
            net_profit,
            interest,
            depreciation,
            profit_before_tax,
            tax_percentage,
            eps,
            dividend_payout,

            equity_capital,
            reserves,
            borrowings,
            total_assets,
            fixed_assets,
            investments,

            operating_activity,
            investing_activity,
            financing_activity,

            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct,
        ) = row

        # ====================================================
        # EQUITY
        # ====================================================

        if equity_capital is not None or reserves is not None:

            equity = (
                (equity_capital or 0)
                + (reserves or 0)
            )

        else:

            equity = None

        # ====================================================
        # PROFITABILITY KPIs
        # ====================================================

        net_profit_margin = percentage(
            net_profit,
            sales
        )

        operating_profit_margin = percentage(
            operating_profit,
            sales
        )

        return_on_equity = percentage(
            net_profit,
            equity
        )

        return_on_assets = percentage(
            net_profit,
            total_assets
        )

        # ROCE
        capital_employed = None

        if equity is not None or borrowings is not None:

            capital_employed = (
                (equity or 0)
                + (borrowings or 0)
            )

        return_on_capital_employed = percentage(
            operating_profit,
            capital_employed
        )

        # EBITDA
        ebitda = None

        if (
            operating_profit is not None
            and depreciation is not None
        ):

            ebitda = (
                operating_profit
                + depreciation
            )

        ebitda_margin = percentage(
            ebitda,
            sales
        )

        # EBIT Margin
        ebit_margin = percentage(
            operating_profit,
            sales
        )

        # Tax Rate
        tax_rate = tax_percentage

        # ====================================================
        # LEVERAGE KPIs
        # ====================================================

        debt_to_equity = safe_divide(
            borrowings,
            equity
        )

        debt_to_assets = percentage(
            borrowings,
            total_assets
        )

        equity_ratio = percentage(
            equity,
            total_assets
        )

        interest_coverage = safe_divide(
            operating_profit,
            interest
        )

        borrowings_to_assets = percentage(
            borrowings,
            total_assets
        )

        net_debt = borrowings

        net_debt_to_equity = safe_divide(
            net_debt,
            equity
        )

        # ====================================================
        # EFFICIENCY KPIs
        # ====================================================

        asset_turnover = safe_divide(
            sales,
            total_assets
        )

        fixed_asset_turnover = safe_divide(
            sales,
            fixed_assets
        )

        investment_turnover = safe_divide(
            sales,
            investments
        )

        depreciation_to_revenue = percentage(
            depreciation,
            sales
        )

        # ====================================================
        # CASH FLOW KPIs
        # ====================================================

        cash_from_operations = operating_activity

        # Investing activity is used as CAPEX proxy.
        capex = None

        if investing_activity is not None:

            capex = abs(investing_activity)

        free_cash_flow = None

        if (
            cash_from_operations is not None
            and capex is not None
        ):

            free_cash_flow = (
                cash_from_operations
                - capex
            )

        cfo_to_net_profit = safe_divide(
            cash_from_operations,
            net_profit
        )

        cfo_to_sales = percentage(
            cash_from_operations,
            sales
        )

        capex_to_cfo = None

        if cash_from_operations not in (None, 0):

            capex_to_cfo = (
                abs(capex / cash_from_operations)
                * 100
            )

        financing_cash_flow = financing_activity

        # ====================================================
        # PER-SHARE KPIs
        # ====================================================

        earnings_per_share = eps

        # Book value per share is not calculated here because
        # the source data does not reliably provide share count.

        book_value_per_share = None

        dividend_per_share = None

        if (
            eps is not None
            and dividend_payout is not None
        ):

            dividend_per_share = (
                eps
                * dividend_payout
                / 100
            )

        earnings_yield = None

        if pe_ratio not in (None, 0):

            earnings_yield = (
                1 / pe_ratio
            ) * 100

        dividend_payout_ratio = dividend_payout

        # ====================================================
        # GROWTH KPIs
        # ====================================================

        previous = None

        # TTM cannot be treated as a normal numeric year.
        try:

            current_year = int(year)

            previous_year = str(
                current_year - 1
            )

            previous = history.get(
                (
                    company_id,
                    previous_year
                )
            )

        except (
            ValueError,
            TypeError
        ):

            previous = None

        revenue_growth = None
        operating_profit_growth = None
        net_profit_growth = None
        eps_growth = None
        asset_growth = None
        equity_growth = None
        debt_growth = None
        cfo_growth = None

        if previous is not None:

            previous_sales = previous[2]

            previous_operating_profit = (
                previous[3]
            )

            previous_net_profit = (
                previous[4]
            )

            previous_eps = previous[9]

            previous_equity = (
                (previous[11] or 0)
                + (previous[12] or 0)
            )

            previous_debt = previous[13]

            previous_assets = previous[14]

            previous_cfo = previous[17]

            revenue_growth = growth(
                sales,
                previous_sales
            )

            operating_profit_growth = growth(
                operating_profit,
                previous_operating_profit
            )

            net_profit_growth = growth(
                net_profit,
                previous_net_profit
            )

            eps_growth = growth(
                eps,
                previous_eps
            )

            asset_growth = growth(
                total_assets,
                previous_assets
            )

            equity_growth = growth(
                equity,
                previous_equity
            )

            debt_growth = growth(
                borrowings,
                previous_debt
            )

            cfo_growth = growth(
                cash_from_operations,
                previous_cfo
            )

        # ====================================================
        # APPEND KPI RECORD
        # ====================================================

        calculated.append(
            (
                company_id,
                year,

                # Profitability
                net_profit_margin,
                operating_profit_margin,
                return_on_equity,
                return_on_assets,
                return_on_capital_employed,
                ebitda_margin,
                ebit_margin,
                tax_rate,

                # Leverage
                debt_to_equity,
                debt_to_assets,
                equity_ratio,
                interest_coverage,
                borrowings_to_assets,
                net_debt_to_equity,

                # Efficiency
                asset_turnover,
                fixed_asset_turnover,
                investment_turnover,
                depreciation_to_revenue,

                # Cash Flow
                cash_from_operations,
                free_cash_flow,
                capex,
                cfo_to_net_profit,
                cfo_to_sales,
                capex_to_cfo,
                financing_cash_flow,

                # Per Share
                earnings_per_share,
                book_value_per_share,
                dividend_per_share,
                earnings_yield,
                dividend_payout_ratio,

                # Valuation
                market_cap_crore,
                enterprise_value_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda,
                dividend_yield_pct,

                # Growth
                revenue_growth,
                operating_profit_growth,
                net_profit_growth,
                eps_growth,
                asset_growth,
                equity_growth,
                debt_growth,
                cfo_growth,
            )
        )

    # ========================================================
    # REFRESH KPI TABLE
    # ========================================================

    cursor.execute(
        "DELETE FROM financial_kpis"
    )

    # ========================================================
    # INSERT
    #
    # IMPORTANT:
    # There are exactly 46 columns and 46 placeholders.
    # ========================================================

    cursor.executemany(
        """
        INSERT INTO financial_kpis (

            company_id,
            year,

            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            return_on_assets_pct,
            return_on_capital_employed_pct,
            ebitda_margin_pct,
            ebit_margin_pct,
            tax_rate_pct,

            debt_to_equity,
            debt_to_assets_pct,
            equity_ratio_pct,
            interest_coverage,
            borrowings_to_assets_pct,
            net_debt_to_equity,

            asset_turnover,
            fixed_asset_turnover,
            investment_turnover,
            depreciation_to_revenue_pct,

            cash_from_operations_cr,
            free_cash_flow_cr,
            capex_cr,
            cfo_to_net_profit,
            cfo_to_sales_pct,
            capex_to_cfo_pct,
            financing_cash_flow_cr,

            earnings_per_share,
            book_value_per_share,
            dividend_per_share,
            earnings_yield_pct,
            dividend_payout_ratio_pct,

            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct,

            revenue_growth_pct,
            operating_profit_growth_pct,
            net_profit_growth_pct,
            eps_growth_pct,
            asset_growth_pct,
            equity_growth_pct,
            debt_growth_pct,
            cfo_growth_pct

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        calculated
    )

    conn.commit()

    # ========================================================
    # FINAL COUNT
    # ========================================================

    count = cursor.execute(
        "SELECT COUNT(*) FROM financial_kpis"
    ).fetchone()[0]

    conn.close()

    return count


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("FINANCIAL KPI ENGINE")
    print("=" * 60)

    print(f"Database: {DB_PATH}")

    count = calculate_kpis()

    print(f"Rows processed: {count}")

    print("KPI calculation completed successfully.")