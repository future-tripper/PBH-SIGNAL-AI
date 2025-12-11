#!/usr/bin/env python3
"""
Compare enrichment results from multiple sources against expected outputs.

Automatically discovers all model_* directories in api_test_outputs/

Usage:
    python compare_all_sources.py
"""

import json
import csv
import ast
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent
EXPECTED_DIR = BASE_DIR / "expected_outputs"
DEV_PIPELINE_DIR = BASE_DIR / "from-dev-pipeline"
API_OUTPUTS_DIR = BASE_DIR / "api_test_outputs"

# TIER 1: Critical/Safety Fields
TIER1_FIELDS = ['flags', 'relevance_label', 'bariatric_context']

# TIER 2: Core Product Fields
TIER2_FIELDS = ['audience_label', 'sentiment_label', 'themes', 'conditions',
                'treatments', 'companies', 'symptoms', 'topics', 'engagement_label']


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
                # Convert relevant fields
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
                }
    return results


def load_api_test3_outputs() -> dict:
    """Load local API test3 outputs keyed by source_id"""
    results = {}
    for path in API_TEST3_DIR.glob("*_enriched.json"):
        source_id = path.stem.replace('_enriched', '')
        with open(path, 'r') as f:
            results[source_id] = json.load(f)
    return results


def load_api_json_dir(dir_path: Path) -> dict:
    """Load API outputs from a directory keyed by source_id"""
    results = {}
    if not dir_path.exists():
        return results
    for path in dir_path.glob("*_enriched.json"):
        source_id = path.stem.replace('_enriched', '')
        with open(path, 'r') as f:
            results[source_id] = json.load(f)
    return results


def compare_value(expected: Any, actual: Any) -> bool:
    """Compare two values (set comparison for lists)"""
    if isinstance(expected, list) and isinstance(actual, list):
        return set(expected) == set(actual)
    return expected == actual


def compare_source(expected: dict, actual: dict, source_id: str) -> dict:
    """Compare a single source against expected"""
    tier1_issues = []
    tier2_issues = []

    for field in TIER1_FIELDS:
        exp_val = expected.get(field)
        act_val = actual.get(field)
        if not compare_value(exp_val, act_val):
            tier1_issues.append({
                'field': field,
                'expected': exp_val,
                'actual': act_val
            })

    for field in TIER2_FIELDS:
        exp_val = expected.get(field)
        act_val = actual.get(field)
        if not compare_value(exp_val, act_val):
            tier2_issues.append({
                'field': field,
                'expected': exp_val,
                'actual': act_val
            })

    return {
        'source_id': source_id,
        'tier1_pass': len(tier1_issues) == 0,
        'tier2_pass': len(tier2_issues) == 0,
        'tier1_issues': tier1_issues,
        'tier2_issues': tier2_issues
    }


def run_comparison(name: str, expected: dict, actual: dict) -> dict:
    """Run full comparison and return results"""
    results = {
        'name': name,
        'total': 0,
        'matched': 0,
        'missing': 0,
        'tier1_pass': 0,
        'tier2_pass': 0,
        'overall_pass': 0,
        'field_issues': {},
        'failures': []
    }

    for source_id, exp_data in expected.items():
        if source_id not in actual:
            results['missing'] += 1
            continue

        results['total'] += 1
        results['matched'] += 1

        comparison = compare_source(exp_data, actual[source_id], source_id)

        if comparison['tier1_pass']:
            results['tier1_pass'] += 1
        if comparison['tier2_pass']:
            results['tier2_pass'] += 1
        if comparison['tier1_pass'] and comparison['tier2_pass']:
            results['overall_pass'] += 1

        # Track field issues
        for issue in comparison['tier1_issues'] + comparison['tier2_issues']:
            field = issue['field']
            results['field_issues'][field] = results['field_issues'].get(field, 0) + 1

        if not (comparison['tier1_pass'] and comparison['tier2_pass']):
            results['failures'].append(comparison)

    # Calculate percentages
    if results['total'] > 0:
        results['tier1_pct'] = results['tier1_pass'] / results['total'] * 100
        results['tier2_pct'] = results['tier2_pass'] / results['total'] * 100
        results['overall_pct'] = results['overall_pass'] / results['total'] * 100
    else:
        results['tier1_pct'] = results['tier2_pct'] = results['overall_pct'] = 0

    return results


def print_results(results: dict, show_failures: bool = False):
    """Print comparison results"""
    print(f"\n{'='*70}")
    print(f"  {results['name']}")
    print(f"{'='*70}")

    if results['missing'] > 0:
        print(f"\n  Missing from source: {results['missing']} (of {results['total'] + results['missing']} expected)")

    t1_status = "PASS" if results['tier1_pct'] >= 90 else "FAIL"
    t2_status = "PASS" if results['tier2_pct'] >= 80 else "FAIL"

    print(f"\n  RESULTS (out of {results['total']} matched):")
    print(f"  {'─'*40}")
    print(f"  Tier 1 (Critical): {results['tier1_pass']}/{results['total']} = {results['tier1_pct']:.1f}%  [{t1_status}] (target ≥90%)")
    print(f"  Tier 2 (Core):     {results['tier2_pass']}/{results['total']} = {results['tier2_pct']:.1f}%  [{t2_status}] (target ≥80%)")
    print(f"  Overall:           {results['overall_pass']}/{results['total']} = {results['overall_pct']:.1f}%")

    if results['field_issues']:
        print(f"\n  ISSUES BY FIELD:")
        sorted_issues = sorted(results['field_issues'].items(), key=lambda x: -x[1])
        for field, count in sorted_issues:
            tier = "T1" if field in TIER1_FIELDS else "T2"
            print(f"    [{tier}] {field}: {count}")

    if show_failures and results['failures']:
        print(f"\n  DETAILED FAILURES ({len(results['failures'])} cases):")
        for f in results['failures'][:10]:  # Show first 10
            print(f"\n    {f['source_id']}:")
            for issue in f['tier1_issues']:
                print(f"      [T1] {issue['field']}: expected={issue['expected']}, actual={issue['actual']}")
            for issue in f['tier2_issues']:
                print(f"      [T2] {issue['field']}: expected={issue['expected']}, actual={issue['actual']}")


def main():
    print("\n" + "="*70)
    print("  V6.1 ENRICHMENT COMPARISON - ALL SOURCES")
    print("="*70)

    # Load expected outputs
    expected = load_expected_outputs()
    print(f"\n  Expected outputs loaded: {len(expected)}")

    # Load all sources
    sources = {}

    # Dev pipeline - auto-discover latest CSV
    try:
        csv_files = list(DEV_PIPELINE_DIR.glob("*.csv"))
        if csv_files:
            latest_csv = sorted(csv_files)[-1]  # Most recent by name
            sources['Dev Pipeline'] = load_dev_pipeline_csv(latest_csv.name)
            print(f"  Dev pipeline loaded: {len(sources['Dev Pipeline'])} records ({latest_csv.name})")
        else:
            print(f"  Dev pipeline: No CSV files found in {DEV_PIPELINE_DIR}")
    except Exception as e:
        print(f"  Dev pipeline: ERROR - {e}")

    # Auto-discover all model_* directories
    for model_dir in sorted(API_OUTPUTS_DIR.glob("model_*")):
        if model_dir.is_dir():
            # Count JSON files to skip empty dirs
            json_count = len(list(model_dir.glob("*_enriched.json")))
            if json_count == 0:
                continue

            # Parse dir name: model_4o_temp01 -> "gpt-4o @ 0.1"
            dir_name = model_dir.name.replace("model_", "")
            name = f"Local: {dir_name}"

            try:
                sources[name] = load_api_json_dir(model_dir)
                print(f"  {name}: {len(sources[name])} records")
            except Exception as e:
                print(f"  {name}: ERROR - {e}")

    # Run comparisons
    all_results = []
    for name, actual in sources.items():
        results = run_comparison(name, expected, actual)
        all_results.append(results)
        print_results(results, show_failures=True)

    # Summary table
    print(f"\n{'='*70}")
    print(f"  SUMMARY COMPARISON")
    print(f"{'='*70}")
    print(f"\n  {'Source':<35} {'T1 %':>8} {'T2 %':>8} {'Overall':>10}")
    print(f"  {'-'*35} {'-'*8} {'-'*8} {'-'*10}")

    for r in all_results:
        t1_icon = "PASS" if r['tier1_pct'] >= 90 else "FAIL"
        t2_icon = "PASS" if r['tier2_pct'] >= 80 else "FAIL"
        print(f"  {r['name']:<35} {r['tier1_pct']:>6.1f}% {r['tier2_pct']:>6.1f}% {r['overall_pct']:>8.1f}%")

    print()


if __name__ == "__main__":
    main()
