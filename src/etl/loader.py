from pathlib import Path
import sqlite3
import pandas as pd

from normaliser import normalize_dataframe


RAW_DATA_DIR = Path("data/raw")
DB_DIR = Path("db")
OUTPUT_DIR = Path("output")

DB_PATH = DB_DIR / "nifty100.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


FILES = [
    ("companies", "companies.xlsx"),
    ("sectors", "sectors.xlsx"),
    ("profitandloss", "profitandloss.xlsx"),
    ("balancesheet", "balancesheet.xlsx"),
    ("cashflow", "cashflow.xlsx"),
    ("analysis", "analysis.xlsx"),
    ("documents", "documents.xlsx"),
    ("prosandcons", "prosandcons.xlsx"),
    ("financial_ratios", "financial_ratios.xlsx"),
    ("peer_groups", "peer_groups.xlsx"),
    ("stock_prices", "stock_prices.xlsx"),
    ("market_cap", "market_cap.xlsx"),
]


TITLE_HEADER_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}


def read_source_file(filename):
    """Read a Bluestock Excel file using its correct header format."""

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")

    if filename in TITLE_HEADER_FILES:
        raw = pd.read_excel(path, header=None)

        columns = raw.iloc[1].tolist()

        df = raw.iloc[2:].copy()
        df.columns = columns

    else:
        df = pd.read_excel(path)

    return df.reset_index(drop=True)


def prepare_dataframe(filename):
    """Read and normalise one source file."""

    df = read_source_file(filename)

    df = normalize_dataframe(df)

    df = df.dropna(how="all")

    df = df.where(pd.notna(df), None)

    return df.reset_index(drop=True)


def create_database():
    """Create a fresh SQLite database."""

    DB_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    schema = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    connection.executescript(schema)

    return connection


def load_table(
    connection,
    table_name,
    filename,
    valid_company_ids=None
):
    """Load one source dataframe into SQLite."""

    df = prepare_dataframe(filename)

    print(
        f"  Columns: {list(df.columns)}"
    )

    print(
        f"  Source rows: {len(df)}"
    )

    rejected = pd.DataFrame()

    # Normalize company IDs.
    if "company_id" in df.columns:

        df["company_id"] = (
            df["company_id"]
            .astype("string")
            .str.strip()
            .replace({
                "AGTL": "ATGL"
            })
        )

    # Validate company IDs against companies master.
    if (
        valid_company_ids is not None
        and "company_id" in df.columns
    ):

        invalid_mask = ~df["company_id"].isin(
            valid_company_ids
        )

        rejected = df[invalid_mask].copy()

        if len(rejected) > 0:

            print(
                f"  Rejected rows: {len(rejected)}"
            )

            print(
                "  Invalid company IDs:",
                sorted(
                    rejected["company_id"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            )

            df = df[~invalid_mask].copy()

    print(
        f"  Rows loaded: {len(df)}"
    )

    if len(df) > 0:

        df.to_sql(
            table_name,
            connection,
            if_exists="append",
            index=False
        )

    return len(df), rejected


def create_load_audit(rows):
    """Create the load audit CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    audit = pd.DataFrame(rows)

    audit.to_csv(
        OUTPUT_DIR / "load_audit.csv",
        index=False
    )


def main():

    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE PLATFORM")
    print("SPRINT 1 - FULL DATA LOAD")
    print("=" * 70)

    connection = create_database()

    audit_rows = []
    rejected_rows = []

    try:

        # --------------------------------------------------
        # Load authoritative company master
        # --------------------------------------------------

        companies_df = prepare_dataframe(
            "companies.xlsx"
        )

        valid_company_ids = set(
            companies_df["id"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        print(
            f"\nCompany master loaded: "
            f"{len(valid_company_ids)} companies"
        )

        # --------------------------------------------------
        # Load all tables
        # --------------------------------------------------

        for table_name, filename in FILES:

            print(
                f"\nLoading {filename}"
            )

            try:

                rows, rejected = load_table(
                    connection,
                    table_name,
                    filename,
                    valid_company_ids
                )

                # Save rejected records in memory.
                if len(rejected) > 0:

                    rejected = rejected.copy()

                    rejected.insert(
                        0,
                        "table_name",
                        table_name
                    )

                    rejected.insert(
                        1,
                        "source_file",
                        filename
                    )

                    rejected_rows.append(
                        rejected
                    )

                audit_rows.append({
                    "table_name": table_name,
                    "source_file": filename,
                    "rows_loaded": rows,
                    "rejected_rows": len(rejected),
                    "severity": (
                        "WARNING"
                        if len(rejected) > 0
                        else "OK"
                    )
                })

            except Exception as exc:

                print(
                    f"  ERROR: {exc}"
                )

                audit_rows.append({
                    "table_name": table_name,
                    "source_file": filename,
                    "rows_loaded": 0,
                    "rejected_rows": "ALL",
                    "severity": "CRITICAL"
                })

                raise

        # --------------------------------------------------
        # Commit
        # --------------------------------------------------

        connection.commit()

        # --------------------------------------------------
        # Foreign-key validation
        # --------------------------------------------------

        print(
            "\nRunning foreign-key validation..."
        )

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print(
            f"Foreign-key violations: "
            f"{len(violations)}"
        )

        if violations:

            for violation in violations[:20]:
                print(violation)

            raise RuntimeError(
                "Foreign-key validation failed."
            )

        # --------------------------------------------------
        # Load audit
        # --------------------------------------------------

        create_load_audit(
            audit_rows
        )

        print(
            "\nLoad audit created:"
        )

        print(
            OUTPUT_DIR / "load_audit.csv"
        )

        # --------------------------------------------------
        # Rejected records
        # --------------------------------------------------

        if rejected_rows:

            rejected_df = pd.concat(
                rejected_rows,
                ignore_index=True
            )

            rejected_df.to_csv(
                OUTPUT_DIR / "load_rejections.csv",
                index=False
            )

            print(
                "\nRejected records created:"
            )

            print(
                OUTPUT_DIR / "load_rejections.csv"
            )

        # --------------------------------------------------
        # Final result
        # --------------------------------------------------

        print(
            "\nDatabase created:"
        )

        print(
            DB_PATH
        )

        print(
            "\nFULL DATA LOAD COMPLETED."
        )

    finally:

        connection.close()


if __name__ == "__main__":
 