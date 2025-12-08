#!/usr/bin/env python3
"""
CSV to Normalized JSON Converter for v6 Testing

Converts CSV rows from data-everything.csv to normalized JSON format
matching the enrichment input schema.

Usage:
    python csv_to_normalized.py                    # Convert all 45 test candidates
    python csv_to_normalized.py --source-id t3_xyz # Convert specific post
    python csv_to_normalized.py --all              # Convert all 1000 posts
"""

import pandas as pd
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


def convert_row_to_normalized(row: pd.Series) -> dict:
    """
    Convert a CSV row to normalized JSON format.

    Maps CSV columns to the normalized schema expected by the enrichment system.
    """

    # Handle NaN values
    def clean_value(val, default=None):
        if pd.isna(val):
            return default
        return val

    def clean_int(val, default=0):
        if pd.isna(val):
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def clean_string(val, default=None):
        if pd.isna(val):
            return default
        return str(val).strip() if val else default

    # Build normalized JSON structure
    normalized = {
        "source": clean_string(row.get('source'), 'unknown'),
        "source_id": clean_string(row.get('source_id'), ''),
        "url": clean_string(row.get('url'), ''),
        "title": clean_string(row.get('title')),
        "text": clean_string(row.get('text'), ''),
        "parent_source": clean_string(row.get('parent_source')),
        "subsource": clean_string(row.get('subsource')),
        "author": {
            "id": clean_string(row.get('author_id'), 'unknown'),
            "name": clean_string(row.get('author_name'), 'Unknown'),
            "handle": clean_string(row.get('author_handle'), 'unknown'),
            "gender": clean_string(row.get('author_gender')),
            "age": clean_int(row.get('author_age')) if not pd.isna(row.get('author_age')) else None,
            "subscribers": clean_int(row.get('author_subscribers')) if not pd.isna(row.get('author_subscribers')) else None
        },
        "country": clean_string(row.get('country')),
        "language": clean_string(row.get('language'), 'eng'),
        "metrics": {
            "likes": clean_int(row.get('likes'), 0),
            "comments": clean_int(row.get('comments'), 0),
            "shares": clean_int(row.get('shares')) if not pd.isna(row.get('shares')) else None
        },
        "sentiment_raw": clean_string(row.get('sentiment')),
        "published_at": clean_string(row.get('published_at'))
    }

    return normalized


def load_test_candidates(candidates_file: Path) -> list:
    """Load the list of test candidate source_ids."""
    df = pd.read_csv(candidates_file)
    return df['source_id'].tolist()


def convert_csv_to_normalized(
    csv_path: Path,
    output_dir: Path,
    source_ids: list = None,
    convert_all: bool = False
):
    """
    Convert CSV rows to normalized JSON files.

    Args:
        csv_path: Path to data-everything.csv
        output_dir: Directory to save normalized JSON files
        source_ids: List of specific source_ids to convert (optional)
        convert_all: If True, convert all rows
    """
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")

    # Filter to specific source_ids if provided
    if source_ids and not convert_all:
        df = df[df['source_id'].isin(source_ids)]
        print(f"Filtered to {len(df)} rows matching provided source_ids")

    if len(df) == 0:
        print("❌ No rows to convert")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    errors = 0

    for idx, row in df.iterrows():
        source_id = row.get('source_id', f'row_{idx}')

        try:
            normalized = convert_row_to_normalized(row)

            # Save to JSON file
            # Sanitize source_id for filename
            safe_filename = str(source_id).replace('/', '_').replace('\\', '_')
            output_path = output_dir / f"{safe_filename}.json"

            with open(output_path, 'w') as f:
                json.dump(normalized, f, indent=2)

            converted += 1

        except Exception as e:
            print(f"❌ Error converting {source_id}: {e}")
            errors += 1

    print()
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"  Converted: {converted}")
    print(f"  Errors: {errors}")
    print(f"  Output directory: {output_dir}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV rows to normalized JSON for v6 testing"
    )
    parser.add_argument(
        "--source-id",
        help="Convert specific source_id only"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Convert all 1000 rows (default: only 45 test candidates)"
    )
    parser.add_argument(
        "--csv",
        default="../phase2/data-everything.csv",
        help="Path to input CSV (default: ../phase2/data-everything.csv)"
    )
    parser.add_argument(
        "--output",
        default="./normalized_inputs",
        help="Output directory (default: ./normalized_inputs)"
    )
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    csv_path = (base_dir / args.csv).resolve()
    output_dir = (base_dir / args.output).resolve()

    # Determine which source_ids to convert
    if args.source_id:
        source_ids = [args.source_id]
    elif args.all:
        source_ids = None  # Will convert all
    else:
        # Load from test candidates
        candidates_file = base_dir / "test_candidates" / "changed_relevance_candidates.csv"
        if candidates_file.exists():
            source_ids = load_test_candidates(candidates_file)
            print(f"Loaded {len(source_ids)} test candidates")
        else:
            print(f"❌ Candidates file not found: {candidates_file}")
            print("   Run extract_test_candidates.py first, or use --all")
            sys.exit(1)

    convert_csv_to_normalized(
        csv_path=csv_path,
        output_dir=output_dir,
        source_ids=source_ids,
        convert_all=args.all
    )


if __name__ == "__main__":
    main()
