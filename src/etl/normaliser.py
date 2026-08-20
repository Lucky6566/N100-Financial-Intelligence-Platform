"""
N100 Financial Intelligence Platform
Sprint 1 - Data Normalisation
"""

from pathlib import Path
import re
import pandas as pd


RAW_DATA_DIR = Path("data/raw")


TITLE_PREFIXES = (
    "Bluestock Fintech",
    "Mkt Fintech",
)


def normalize_ticker(value):
    """Normalize a company ticker/company identifier."""
    if pd.isna(value):
        return None

    value = str(value).strip().upper()
    value = re.sub(r"\s+", "", value)

    return value if value else None


def normalize_year(value):
    """Normalize annual years while preserving TTM."""

    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    # Preserve Trailing Twelve Months records.
    if text == "TTM":
        return "TTM"

    # Numeric year.
    try:
        numeric = float(value)

        if 1900 <= numeric <= 2100:
            return str(int(numeric))

    except (ValueError, TypeError):
        pass

    # Four-digit year inside text.
    match = re.search(r"\b(19|20)\d{2}\b", text)

    if match:
        return match.group()

    # Formats such as Mar-14 / Mar 14.
    match = re.search(
        r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
        r"[A-Z]*[\s\-/]*(\d{2})",
        text,
        re.IGNORECASE
    )

    if match:
        two_digit_year = int(match.group(2))

        if two_digit_year >= 90:
            return str(1900 + two_digit_year)

        return str(2000 + two_digit_year)

    return None
def clean_column_name(column):
    """Convert one column name into a safe standard form."""
    value = str(column).strip().lower()

    value = value.replace("—", "_")
    value = value.replace("–", "_")
    value = value.replace("-", "_")
    value = value.replace("/", "_")
    value = re.sub(r"\s+", "_", value)

    return value.strip("_")


def clean_column_names(df):
    """Standardise dataframe column names safely."""
    df = df.copy()

    df.columns = [
        clean_column_name(column)
        for column in df.columns
    ]

    return df


def remove_embedded_title(df):
    """
    Remove embedded title/header rows from Bluestock workbooks.

    Some files contain a title as the first data row.
    Other files contain the title as the only Excel header.
    """
    df = df.copy()

    # Case 1: title appears as the first data row.
    if len(df) > 0 and len(df.columns) == 1:
        first_value = str(df.iloc[0, 0]).strip()

        if first_value.startswith(TITLE_PREFIXES):
            df = df.iloc[1:].reset_index(drop=True)

    # Case 2: title itself became the column name.
    if len(df.columns) == 1:
        column_name = str(df.columns[0]).strip()

        if column_name.startswith(TITLE_PREFIXES):
            df = df.iloc[1:].reset_index(drop=True)

    return df


def normalize_dataframe(df):
    """Apply general normalisation to a dataframe."""
    df = remove_embedded_title(df)
    df = clean_column_names(df)

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(
            normalize_ticker
        )

    if "year" in df.columns:
        df["year"] = df["year"].apply(
            normalize_year
        )

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    return df


def load_excel(filename):
    """Load and normalise one Excel file."""
    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {path}"
        )

    df = pd.read_excel(path)

    return normalize_dataframe(df)


if __name__ == "__main__":

    print("N100 normaliser loaded successfully.")

    files = sorted(RAW_DATA_DIR.glob("*.xlsx"))

    print(f"Excel files found: {len(files)}")

    for file in files:
        try:
            df = load_excel(file.name)

            print(
                f"{file.name}: "
                f"{len(df)} records | "
                f"{len(df.columns)} columns"
            )

        except Exception as exc:
            print(
                f"{file.name}: ERROR - {exc}"
            )