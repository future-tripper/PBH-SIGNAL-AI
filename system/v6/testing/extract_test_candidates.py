#!/usr/bin/env python3
"""
Extract test candidates from real pipeline data for v6 validation.

This script identifies posts that SHOULD change under v6 relevance logic:
1. Posts with bariatric keywords currently marked not_relevant
2. Posts mentioning PBH treatments (acarbose, diazoxide, octreotide)
3. Posts mentioning GLP-1s with bariatric context

Usage:
    python extract_test_candidates.py <input_csv> <output_dir>

Example:
    python extract_test_candidates.py ../phase2/data-everything.csv ./test_candidates/
"""

import pandas as pd
import json
import re
import sys
from pathlib import Path

# Treatment patterns for matching
PBH_TREATMENTS = [
    r'\bavexitide\b', r'\bexendin.?9.?39\b',
    r'\bacarbose\b', r'\bprecose\b', r'\bglucobay\b', r'\bacrobose\b', r'\bacarobose\b',
    r'\bdiazoxide\b', r'\bproglycem\b',
    r'\boctreotide\b', r'\bsandostatin\b'
]

GLP1_TREATMENTS = [
    r'\bsemaglutide\b', r'\bozempic\b', r'\bwegovy\b', r'\bwegoivy\b',
    r'\btirzepatide\b', r'\bmounjaro\b', r'\bzepbound\b',
    r'\bdulaglutide\b', r'\btrulicity\b',
    r'\bliraglutide\b', r'\bvictoza\b', r'\bsaxenda\b',
    r'\bexenatide\b', r'\bbyetta\b', r'\bbydureon\b'
]

BARIATRIC_KEYWORDS = [
    r'\bbariatric\b', r'\bgastric.?bypass\b', r'\bgastric.?sleeve\b',
    r'\broux.?en.?y\b', r'\brny\b', r'\brygb\b', r'\bvsg\b',
    r'\bweight.?loss.?surgery\b', r'\bwls\b', r'\bgastrectomy\b',
    r'\bpost.?op\b', r'\bsince.?my.?surgery\b', r'\bafter.?my.?surgery\b',
    r'\bduodenal.?switch\b', r'\blap.?band\b'
]

PBH_KEYWORDS = [
    r'\bpbh\b', r'\bpost.?bariatric.?hypoglycemia\b',
    r'\blate.?dumping\b', r'\breactive.?hypoglycemia\b'
]


def has_pattern(text, patterns):
    """Check if text matches any pattern in list."""
    if pd.isna(text):
        return False
    text = str(text).lower()
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def categorize_post(row):
    """Categorize a post based on v6 relevance criteria."""
    text = str(row.get('text', '')) + ' ' + str(row.get('title', ''))

    categories = []

    # Check for PBH treatments
    if has_pattern(text, PBH_TREATMENTS):
        categories.append('pbh_treatment')

    # Check for GLP-1 treatments
    if has_pattern(text, GLP1_TREATMENTS):
        categories.append('glp1_treatment')

    # Check for bariatric context
    if has_pattern(text, BARIATRIC_KEYWORDS):
        categories.append('bariatric_context')

    # Check for PBH mentions
    if has_pattern(text, PBH_KEYWORDS):
        categories.append('pbh_mention')

    return categories


def determine_expected_v6_relevance(row, categories):
    """Determine what v6 relevance should be based on categories."""
    # RELEVANT triggers
    if 'pbh_mention' in categories:
        return 'relevant', 'PBH explicitly mentioned'
    if 'pbh_treatment' in categories:
        return 'relevant', 'PBH treatment mentioned (acarbose, diazoxide, octreotide, or avexitide)'
    if 'bariatric_context' in categories and 'glp1_treatment' in categories:
        return 'relevant', 'Bariatric context + GLP-1 treatment'

    # BORDERLINE triggers
    if 'bariatric_context' in categories:
        return 'borderline', 'Bariatric context without PBH indicators'
    if 'glp1_treatment' in categories:
        return 'borderline', 'GLP-1 treatment without bariatric context (needs review)'

    return 'not_relevant', 'No relevant triggers found'


def extract_candidates(input_csv, output_dir):
    """Extract test candidates from CSV."""
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} rows")

    # Get current relevance if available
    if 'relevance_label' not in df.columns:
        df['relevance_label'] = 'unknown'

    candidates = []

    for idx, row in df.iterrows():
        categories = categorize_post(row)

        if not categories:
            continue

        current_rel = row.get('relevance_label', 'unknown')
        expected_rel, reason = determine_expected_v6_relevance(row, categories)

        # Flag if relevance would change
        would_change = (current_rel == 'not_relevant' and expected_rel in ['relevant', 'borderline'])

        candidates.append({
            'row_index': idx,
            'source_id': row.get('source_id', ''),
            'source': row.get('source', ''),
            'title': str(row.get('title', ''))[:100],
            'text_preview': str(row.get('text', ''))[:200],
            'current_relevance': current_rel,
            'expected_v6_relevance': expected_rel,
            'v6_reason': reason,
            'categories': categories,
            'would_change': would_change
        })

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save all candidates
    candidates_df = pd.DataFrame(candidates)
    candidates_df.to_csv(output_path / 'all_test_candidates.csv', index=False)
    print(f"\nSaved {len(candidates)} total candidates to all_test_candidates.csv")

    # Filter to posts that would change
    changed = candidates_df[candidates_df['would_change'] == True]
    changed.to_csv(output_path / 'changed_relevance_candidates.csv', index=False)
    print(f"Saved {len(changed)} posts that would change relevance")

    # Summary by category
    print("\n=== Summary ===")
    print(f"Total candidates with relevant triggers: {len(candidates)}")
    print(f"Posts that would change relevance: {len(changed)}")

    # Category breakdown
    category_counts = {}
    for c in candidates:
        for cat in c['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\nCategory breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Expected relevance breakdown
    print("\nExpected v6 relevance distribution:")
    for rel in ['relevant', 'borderline', 'not_relevant']:
        count = len([c for c in candidates if c['expected_v6_relevance'] == rel])
        print(f"  {rel}: {count}")

    return candidates_df


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_test_candidates.py <input_csv> <output_dir>")
        print("Example: python extract_test_candidates.py ../phase2/data-everything.csv ./test_candidates/")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_dir = sys.argv[2]

    extract_candidates(input_csv, output_dir)
