from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


MULTI_VALUE_COLUMNS = ["platforms", "categories", "genres", "steamspy_tags"]
TEXT_COLUMNS_WITH_UNKNOWN = ["developer", "publisher"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean and preprocess the Steam dataset for MongoDB import."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/steam.csv"),
        help="Path to the raw Steam CSV file.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/processed/games_cleaned.json"),
        help="Path to the cleaned JSON output file.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/processed/games_cleaned.csv"),
        help="Path to the cleaned CSV output file.",
    )
    return parser.parse_args()


def ensure_output_dirs(*paths: Path) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)


def clean_text_value(value: Any, fallback: str = "Unknown") -> str:
    if pd.isna(value):
        return fallback

    text = str(value).strip()
    if text == "":
        return fallback

    return text


def split_multi_value_field(value: Any) -> list[str]:
    """
    Convert semicolon-separated strings into clean arrays.
    Examples:
        "Action;Adventure" -> ["Action", "Adventure"]
        "Windows;Mac;Linux" -> ["Windows", "Mac", "Linux"]
        NaN / "" -> []
    """
    if pd.isna(value):
        return []

    text = str(value).strip()
    if not text:
        return []

    items = [item.strip() for item in text.split(";")]
    items = [item for item in items if item]

    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def normalize_date(value: Any) -> str | None:
    """
    Convert release_date to ISO format YYYY-MM-DD.
    Returns None if parsing fails.
    """
    if pd.isna(value):
        return None

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None

    return parsed.strftime("%Y-%m-%d")


def parse_owners_range(value: Any) -> tuple[int | None, int | None]:
    """
    Convert owners range string like '1000000-2000000'
    into numeric min/max fields.
    """
    if pd.isna(value):
        return None, None

    text = str(value).strip()
    if not text:
        return None, None

    match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", text)
    if not match:
        return None, None

    owners_min = int(match.group(1))
    owners_max = int(match.group(2))
    return owners_min, owners_max


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    int_columns = [
        "appid",
        "english",
        "required_age",
        "achievements",
        "positive_ratings",
        "negative_ratings",
        "average_playtime",
        "median_playtime",
    ]
    float_columns = ["price"]

    for col in int_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)

    return df


def build_documents(df: pd.DataFrame) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        doc = {
            "appid": int(row["appid"]),
            "name": clean_text_value(row["name"], fallback="Unknown Game"),
            "release_date": row["release_date"],
            "english": bool(row["english"]),
            "developer": clean_text_value(row["developer"]),
            "publisher": clean_text_value(row["publisher"]),
            "platforms": row["platforms"],
            "required_age": int(row["required_age"]),
            "categories": row["categories"],
            "genres": row["genres"],
            "steamspy_tags": row["steamspy_tags"],
            "achievements": int(row["achievements"]),
            "positive_ratings": int(row["positive_ratings"]),
            "negative_ratings": int(row["negative_ratings"]),
            "average_playtime": int(row["average_playtime"]),
            "median_playtime": int(row["median_playtime"]),
            "owners": clean_text_value(row["owners"], fallback="Unknown"),
            "owners_min": row["owners_min"],
            "owners_max": row["owners_max"],
            "price": float(row["price"]),
        }
        documents.append(doc)

    return documents


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    ensure_output_dirs(args.output_json, args.output_csv)

    df = pd.read_csv(args.input)

    # 1) Handle missing / empty text values
    for col in TEXT_COLUMNS_WITH_UNKNOWN:
        df[col] = df[col].apply(clean_text_value)

    # Name should never be empty in output
    df["name"] = df["name"].apply(lambda x: clean_text_value(x, fallback="Unknown Game"))

    # 2) Multi-value fields -> arrays
    for col in MULTI_VALUE_COLUMNS:
        df[col] = df[col].apply(split_multi_value_field)

    # 3) Standardize date
    df["release_date"] = df["release_date"].apply(normalize_date)

    # 4) Owners range -> numeric min/max
    owners_ranges = df["owners"].apply(parse_owners_range)
    df["owners_min"] = owners_ranges.apply(lambda x: x[0])
    df["owners_max"] = owners_ranges.apply(lambda x: x[1])

    # 5) Numeric columns
    df = convert_numeric_columns(df)

    # 6) Export cleaned CSV
    # For CSV, arrays are serialized as JSON strings for readability/reusability
    csv_df = df.copy()
    for col in MULTI_VALUE_COLUMNS:
        csv_df[col] = csv_df[col].apply(json.dumps)

    csv_df.to_csv(args.output_csv, index=False)

    # 7) Export cleaned JSON (best for MongoDB import)
    documents = build_documents(df)
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    # 8) Simple report
    print("Preprocessing completed successfully.")
    print(f"Input rows: {len(df)}")
    print(f"JSON output: {args.output_json}")
    print(f"CSV output:  {args.output_csv}")
    print()
    print("Quick checks:")
    print(f"- developer missing after cleaning: {(df['developer'] == 'Unknown').sum()}")
    print(f"- publisher missing after cleaning: {(df['publisher'] == 'Unknown').sum()}")
    print(f"- release_date null after parsing: {df['release_date'].isna().sum()}")
    print(f"- duplicate appid count: {df['appid'].duplicated().sum()}")
    print(f"- duplicate name count: {df['name'].duplicated().sum()}")


if __name__ == "__main__":
    main()