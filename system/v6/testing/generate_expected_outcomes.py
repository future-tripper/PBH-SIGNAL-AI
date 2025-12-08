#!/usr/bin/env python3
"""
Generate Expected Outcomes Manifest for v6 Testing

Creates v6_expected_outcomes.json based on the test candidates and v6 relevance rules.

Usage:
    python generate_expected_outcomes.py
"""

import pandas as pd
import json
import re
from pathlib import Path


# Treatment patterns (same as extract_test_candidates.py)
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

BARIATRIC_STRONG = [
    r'\bbariatric\b', r'\bgastric.?bypass\b', r'\bgastric.?sleeve\b',
    r'\broux.?en.?y\b', r'\brny\b', r'\brygb\b', r'\bvsg\b',
    r'\bweight.?loss.?surgery\b', r'\bwls\b', r'\bgastrectomy\b',
    r'\bduodenal.?switch\b', r'\blap.?band\b', r'\bsadi\b', r'\boagb\b'
]

BARIATRIC_WEAK = [
    r'\bpost.?op\b', r'\bsince.?my.?surgery\b', r'\bafter.?my.?surgery\b',
    r'\bafter.?my.?procedure\b', r'\bmy.?operation\b'
]

PBH_KEYWORDS = [
    r'\bpbh\b', r'\bpost.?bariatric.?hypoglycemia\b',
    r'\blate.?dumping\b', r'\breactive.?hypoglycemia\b',
    r'\bpostprandial.?hypoglycemia\b'
]


def has_pattern(text, patterns):
    """Check if text matches any pattern in list."""
    if pd.isna(text):
        return False
    text = str(text).lower()
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def find_treatments(text, patterns, names):
    """Find which treatments are mentioned."""
    if pd.isna(text):
        return []
    text = str(text).lower()
    found = []

    treatment_map = {
        'avexitide': [r'\bavexitide\b', r'\bexendin.?9.?39\b'],
        'acarbose': [r'\bacarbose\b', r'\bprecose\b', r'\bglucobay\b', r'\bacrobose\b', r'\bacarobose\b'],
        'diazoxide': [r'\bdiazoxide\b', r'\bproglycem\b'],
        'octreotide': [r'\boctreotide\b', r'\bsandostatin\b'],
        'semaglutide': [r'\bsemaglutide\b', r'\bozempic\b', r'\bwegovy\b', r'\bwegoivy\b'],
        'tirzepatide': [r'\btirzepatide\b', r'\bmounjaro\b', r'\bzepbound\b'],
        'dulaglutide': [r'\bdulaglutide\b', r'\btrulicity\b'],
        'liraglutide': [r'\bliraglutide\b', r'\bvictoza\b', r'\bsaxenda\b'],
        'exenatide': [r'\bexenatide\b', r'\bbyetta\b', r'\bbydureon\b']
    }

    for treatment, patterns in treatment_map.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            found.append(treatment)

    return found


def determine_expected_outcomes(row):
    """
    Determine expected v6 outcomes for a single post.

    Returns dict with:
    - expected_relevance_label
    - expected_bariatric_context
    - expected_treatments
    - test_category
    - v6_rule
    """
    title = str(row.get('title', '')) if not pd.isna(row.get('title')) else ''
    text = str(row.get('text', '')) if not pd.isna(row.get('text')) else ''
    combined = f"{title} {text}"

    # Detect patterns
    has_pbh_mention = has_pattern(combined, PBH_KEYWORDS)
    has_pbh_treatment = has_pattern(combined, PBH_TREATMENTS)
    has_glp1_treatment = has_pattern(combined, GLP1_TREATMENTS)
    has_bariatric_strong = has_pattern(combined, BARIATRIC_STRONG)
    has_bariatric_weak = has_pattern(combined, BARIATRIC_WEAK)

    # Find specific treatments
    found_treatments = find_treatments(combined, None, None)

    # Determine bariatric_context
    if has_pbh_mention or has_bariatric_strong:
        expected_bariatric_context = "strong"
    elif has_bariatric_weak:
        expected_bariatric_context = "weak"
    else:
        expected_bariatric_context = "none"

    # Determine relevance_label and category using v6 rules
    if has_pbh_mention:
        return {
            "expected_relevance_label": "relevant",
            "expected_bariatric_context": expected_bariatric_context,
            "expected_treatments": found_treatments,
            "test_category": "pbh_mention",
            "v6_rule": "PBH/reactive hypoglycemia explicitly mentioned → relevant"
        }

    if has_pbh_treatment:
        return {
            "expected_relevance_label": "relevant",
            "expected_bariatric_context": expected_bariatric_context,
            "expected_treatments": found_treatments,
            "test_category": "pbh_treatment",
            "v6_rule": "PBH treatment (acarbose/diazoxide/octreotide/avexitide) mentioned → relevant"
        }

    if has_bariatric_strong and has_glp1_treatment:
        return {
            "expected_relevance_label": "relevant",
            "expected_bariatric_context": "strong",
            "expected_treatments": found_treatments,
            "test_category": "glp1_with_bariatric",
            "v6_rule": "Strong bariatric context + GLP-1 treatment → relevant"
        }

    if has_bariatric_strong:
        return {
            "expected_relevance_label": "borderline",
            "expected_bariatric_context": "strong",
            "expected_treatments": found_treatments,
            "test_category": "bariatric_context_only",
            "v6_rule": "Strong bariatric context without PBH indicators → borderline"
        }

    if has_glp1_treatment:
        return {
            "expected_relevance_label": "borderline",
            "expected_bariatric_context": expected_bariatric_context,
            "expected_treatments": found_treatments,
            "test_category": "glp1_only",
            "v6_rule": "GLP-1 treatment without bariatric context → borderline (needs review)"
        }

    if has_bariatric_weak:
        return {
            "expected_relevance_label": "borderline",
            "expected_bariatric_context": "weak",
            "expected_treatments": found_treatments,
            "test_category": "weak_bariatric",
            "v6_rule": "Weak bariatric context → borderline"
        }

    # Default: not_relevant (should not happen for our test candidates)
    return {
        "expected_relevance_label": "not_relevant",
        "expected_bariatric_context": "none",
        "expected_treatments": found_treatments,
        "test_category": "no_triggers",
        "v6_rule": "No relevant triggers found"
    }


def generate_manifest(candidates_csv: Path, data_csv: Path, output_path: Path):
    """Generate the expected outcomes manifest."""

    # Load test candidates
    candidates_df = pd.read_csv(candidates_csv)
    source_ids = candidates_df['source_id'].tolist()
    print(f"Loaded {len(source_ids)} test candidates")

    # Load full data
    data_df = pd.read_csv(data_csv)
    print(f"Loaded {len(data_df)} rows from data CSV")

    # Filter to test candidates
    test_df = data_df[data_df['source_id'].isin(source_ids)]
    print(f"Matched {len(test_df)} rows")

    # Generate expected outcomes
    test_posts = []
    category_counts = {}

    for idx, row in test_df.iterrows():
        source_id = row['source_id']
        outcomes = determine_expected_outcomes(row)

        test_post = {
            "source_id": source_id,
            "title_preview": str(row.get('title', ''))[:50] if not pd.isna(row.get('title')) else None,
            **outcomes
        }
        test_posts.append(test_post)

        # Count categories
        cat = outcomes['test_category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Create manifest
    manifest = {
        "version": "6.0",
        "generated_at": pd.Timestamp.now().isoformat(),
        "total_tests": len(test_posts),
        "category_breakdown": category_counts,
        "expected_results": {
            "relevant": len([p for p in test_posts if p['expected_relevance_label'] == 'relevant']),
            "borderline": len([p for p in test_posts if p['expected_relevance_label'] == 'borderline']),
            "not_relevant": len([p for p in test_posts if p['expected_relevance_label'] == 'not_relevant'])
        },
        "test_posts": test_posts
    }

    # Save manifest
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print()
    print("=" * 60)
    print(f"Generated manifest: {output_path}")
    print(f"Total tests: {len(test_posts)}")
    print()
    print("Category breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print()
    print("Expected relevance distribution:")
    print(f"  relevant: {manifest['expected_results']['relevant']}")
    print(f"  borderline: {manifest['expected_results']['borderline']}")
    print(f"  not_relevant: {manifest['expected_results']['not_relevant']}")
    print("=" * 60)


def main():
    base_dir = Path(__file__).parent

    candidates_csv = base_dir / "test_candidates" / "changed_relevance_candidates.csv"
    data_csv = base_dir.parent.parent / "v5" / "testing" / "phase2" / "data-everything.csv"
    output_path = base_dir / "v6_expected_outcomes.json"

    generate_manifest(candidates_csv, data_csv, output_path)


if __name__ == "__main__":
    main()
