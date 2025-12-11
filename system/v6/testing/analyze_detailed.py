#!/usr/bin/env python3
"""
Enhanced analysis of enrichment results with precision/recall metrics.

Goes beyond pass/fail to show:
- For list fields: precision, recall, over/under-extraction patterns
- For scalar fields: accuracy, confusion matrix

Usage:
    python analyze_detailed.py
"""

import json
import csv
import ast
from pathlib import Path
from collections import defaultdict
from typing import Any

BASE_DIR = Path(__file__).parent
EXPECTED_DIR = BASE_DIR / "expected_outputs"
DEV_PIPELINE_DIR = BASE_DIR / "from-dev-pipeline"

# Fields to analyze
LIST_FIELDS = ['themes', 'topics', 'symptoms', 'conditions', 'treatments', 'companies', 'flags', 'emotions', 'intent']
SCALAR_FIELDS = ['relevance_label', 'bariatric_context', 'audience_label', 'sentiment_label', 'engagement_label']

# Tier classification
TIER1_FIELDS = ['flags', 'relevance_label', 'bariatric_context']
TIER2_FIELDS = ['audience_label', 'sentiment_label', 'themes', 'conditions', 'treatments', 'companies', 'symptoms', 'topics', 'engagement_label', 'emotions', 'intent']


def parse_csv_array(value: str) -> list:
    """Parse CSV array string like '["a","b"]' to Python list"""
    if not value or value == '[]':
        return []
    try:
        return ast.literal_eval(value)
    except:
        return []


def load_expected_outputs() -> dict:
    """Load all expected outputs keyed by source_id"""
    expected = {}
    for path in EXPECTED_DIR.glob("*_enriched.json"):
        source_id = path.stem.replace('_enriched', '')
        with open(path, 'r') as f:
            expected[source_id] = json.load(f)
    return expected


def load_dev_pipeline_csv(filename: str) -> dict:
    """Load dev pipeline CSV and return dict keyed by source_id"""
    results = {}
    csv_path = DEV_PIPELINE_DIR / filename

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_id = row.get('source_id')
            if source_id:
                results[source_id] = {
                    'source_id': source_id,
                    'relevance_label': row.get('relevance_label'),
                    'bariatric_context': row.get('bariatric_context'),
                    'audience_label': row.get('audience_label'),
                    'sentiment_label': row.get('sentiment_label'),
                    'engagement_label': row.get('engagement_label'),
                    'flags': parse_csv_array(row.get('flags', '[]')),
                    'themes': parse_csv_array(row.get('themes', '[]')),
                    'topics': parse_csv_array(row.get('topics', '[]')),
                    'symptoms': parse_csv_array(row.get('symptoms', '[]')),
                    'treatments': parse_csv_array(row.get('treatments', '[]')),
                    'conditions': parse_csv_array(row.get('conditions', '[]')),
                    'companies': parse_csv_array(row.get('companies', '[]')),
                    'emotions': parse_csv_array(row.get('emotions', '[]')),
                    'intent': parse_csv_array(row.get('intent', '[]')),
                }
    return results


def calculate_list_metrics(expected: list, actual: list) -> dict:
    """Calculate precision, recall, and extraction details for a list field"""
    expected_set = set(expected) if expected else set()
    actual_set = set(actual) if actual else set()

    correct = expected_set & actual_set
    over_extracted = actual_set - expected_set
    under_extracted = expected_set - actual_set

    # Precision: of what we extracted, how much was correct?
    precision = len(correct) / len(actual_set) if actual_set else 1.0

    # Recall: of what should be there, how much did we find?
    recall = len(correct) / len(expected_set) if expected_set else 1.0

    return {
        'precision': precision,
        'recall': recall,
        'correct': list(correct),
        'over_extracted': list(over_extracted),
        'under_extracted': list(under_extracted),
        'expected_count': len(expected_set),
        'actual_count': len(actual_set),
        'correct_count': len(correct)
    }


def analyze_list_field(expected_all: dict, actual_all: dict, field: str) -> dict:
    """Analyze a list field across all test cases"""
    total_precision = 0
    total_recall = 0
    count = 0

    over_freq = defaultdict(int)
    under_freq = defaultdict(int)

    case_details = []

    for source_id, exp_data in expected_all.items():
        if source_id not in actual_all:
            continue

        exp_val = exp_data.get(field, [])
        act_val = actual_all[source_id].get(field, [])

        metrics = calculate_list_metrics(exp_val, act_val)

        total_precision += metrics['precision']
        total_recall += metrics['recall']
        count += 1

        for item in metrics['over_extracted']:
            over_freq[item] += 1
        for item in metrics['under_extracted']:
            under_freq[item] += 1

        if metrics['over_extracted'] or metrics['under_extracted']:
            case_details.append({
                'source_id': source_id,
                'expected': exp_val,
                'actual': act_val,
                'over': metrics['over_extracted'],
                'under': metrics['under_extracted']
            })

    return {
        'avg_precision': total_precision / count if count else 0,
        'avg_recall': total_recall / count if count else 0,
        'over_freq': dict(sorted(over_freq.items(), key=lambda x: -x[1])),
        'under_freq': dict(sorted(under_freq.items(), key=lambda x: -x[1])),
        'case_details': case_details,
        'total_cases': count
    }


def analyze_scalar_field(expected_all: dict, actual_all: dict, field: str) -> dict:
    """Analyze a scalar field across all test cases"""
    correct = 0
    total = 0

    confusion = defaultdict(int)
    case_details = []

    for source_id, exp_data in expected_all.items():
        if source_id not in actual_all:
            continue

        exp_val = exp_data.get(field)
        act_val = actual_all[source_id].get(field)

        total += 1
        if exp_val == act_val:
            correct += 1
        else:
            confusion[f"{exp_val} → {act_val}"] += 1
            case_details.append({
                'source_id': source_id,
                'expected': exp_val,
                'actual': act_val
            })

    return {
        'accuracy': correct / total if total else 0,
        'correct': correct,
        'total': total,
        'confusion': dict(sorted(confusion.items(), key=lambda x: -x[1])),
        'case_details': case_details
    }


def print_list_field_report(field: str, analysis: dict, tier: str):
    """Print detailed report for a list field"""
    print(f"\n{'='*70}")
    print(f"  [{tier}] {field.upper()}")
    print(f"{'='*70}")

    print(f"\n  Precision: {analysis['avg_precision']*100:.1f}% (correct / extracted)")
    print(f"  Recall:    {analysis['avg_recall']*100:.1f}% (correct / expected)")

    if analysis['over_freq']:
        print(f"\n  OVER-EXTRACTION (added but shouldn't be):")
        for item, count in list(analysis['over_freq'].items())[:10]:
            print(f"    - \"{item}\": {count} times")

    if analysis['under_freq']:
        print(f"\n  UNDER-EXTRACTION (missed but should be there):")
        for item, count in list(analysis['under_freq'].items())[:10]:
            print(f"    - \"{item}\": {count} times")


def print_scalar_field_report(field: str, analysis: dict, tier: str):
    """Print detailed report for a scalar field"""
    print(f"\n{'='*70}")
    print(f"  [{tier}] {field.upper()}")
    print(f"{'='*70}")

    print(f"\n  Accuracy: {analysis['accuracy']*100:.1f}% ({analysis['correct']}/{analysis['total']})")

    if analysis['confusion']:
        print(f"\n  Confusion (expected → actual):")
        for pattern, count in list(analysis['confusion'].items())[:10]:
            print(f"    - {pattern}: {count} times")


def main():
    print("\n" + "="*70)
    print("  V6.1 ENHANCED ANALYSIS - PRECISION/RECALL METRICS")
    print("="*70)

    # Load data
    expected = load_expected_outputs()
    print(f"\n  Expected outputs loaded: {len(expected)}")

    # Find the latest CSV
    csv_files = list(DEV_PIPELINE_DIR.glob("*2025-12-11*.csv"))
    if not csv_files:
        csv_files = list(DEV_PIPELINE_DIR.glob("*.csv"))

    if not csv_files:
        print("  ERROR: No CSV files found in from-dev-pipeline/")
        return

    csv_file = sorted(csv_files)[-1]  # Most recent
    print(f"  Loading: {csv_file.name}")

    actual = load_dev_pipeline_csv(csv_file.name)
    print(f"  Actual outputs loaded: {len(actual)}")

    # Analyze each field
    list_results = {}
    scalar_results = {}

    for field in LIST_FIELDS:
        list_results[field] = analyze_list_field(expected, actual, field)

    for field in SCALAR_FIELDS:
        scalar_results[field] = analyze_scalar_field(expected, actual, field)

    # Print Tier 1 fields first
    print("\n" + "="*70)
    print("  TIER 1: CRITICAL/SAFETY FIELDS (target ≥90%)")
    print("="*70)

    for field in TIER1_FIELDS:
        tier = "T1"
        if field in scalar_results:
            print_scalar_field_report(field, scalar_results[field], tier)
        elif field in list_results:
            print_list_field_report(field, list_results[field], tier)

    # Print Tier 2 fields
    print("\n" + "="*70)
    print("  TIER 2: CORE PRODUCT FIELDS (target ≥80%)")
    print("="*70)

    for field in TIER2_FIELDS:
        tier = "T2"
        if field in scalar_results:
            print_scalar_field_report(field, scalar_results[field], tier)
        elif field in list_results:
            print_list_field_report(field, list_results[field], tier)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    print(f"\n  {'Field':<25} {'Metric':<12} {'Score':>10} {'Status':>10}")
    print(f"  {'-'*25} {'-'*12} {'-'*10} {'-'*10}")

    for field in TIER1_FIELDS:
        if field in scalar_results:
            score = scalar_results[field]['accuracy'] * 100
            status = "✅ PASS" if score >= 90 else "❌ FAIL"
            print(f"  {field:<25} {'Accuracy':<12} {score:>9.1f}% {status:>10}")
        elif field in list_results:
            prec = list_results[field]['avg_precision'] * 100
            rec = list_results[field]['avg_recall'] * 100
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
            status = "✅ PASS" if f1 >= 90 else "❌ FAIL"
            print(f"  {field:<25} {'F1':<12} {f1:>9.1f}% {status:>10}")

    print()

    for field in TIER2_FIELDS:
        if field in scalar_results:
            score = scalar_results[field]['accuracy'] * 100
            status = "✅ PASS" if score >= 80 else "❌ FAIL"
            print(f"  {field:<25} {'Accuracy':<12} {score:>9.1f}% {status:>10}")
        elif field in list_results:
            prec = list_results[field]['avg_precision'] * 100
            rec = list_results[field]['avg_recall'] * 100
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
            status = "✅ PASS" if f1 >= 80 else "❌ FAIL"
            print(f"  {field:<25} {'F1':<12} {f1:>9.1f}% {status:>10}")

    print()


if __name__ == "__main__":
    main()
