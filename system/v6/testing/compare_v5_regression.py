#!/usr/bin/env python3
"""
Compare v5 regression test outputs against expected outputs.

Usage:
    python compare_v5_regression.py              # Compare all results
    python compare_v5_regression.py --details    # Show detailed failures
    python compare_v5_regression.py --category ae-test-cases  # Compare specific category
"""

import argparse
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent
V5_DATA_DIR = BASE_DIR / "v5-regression-test-data"
EXPECTED_DIR = V5_DATA_DIR / "expected-outputs"
OUTPUT_DIR = BASE_DIR / "api_test_outputs" / "v5_regression_v61"

# Categories
CATEGORIES = [
    "ae-test-cases",
    "classification-tests",
    "dictionary-tests",
    "edge-cases",
    "flag-tests",
    "platform-coverage"
]

# TIER 1: Critical/Safety Fields
TIER1_FIELDS = ['flags', 'relevance_label', 'bariatric_context']

# TIER 2: Core Product Fields
TIER2_FIELDS = ['audience_label', 'sentiment_label', 'themes', 'conditions',
                'treatments', 'companies', 'symptoms', 'topics', 'engagement_label']


def compare_value(expected: Any, actual: Any) -> bool:
    """Compare two values (set comparison for lists)"""
    if isinstance(expected, list) and isinstance(actual, list):
        return set(expected) == set(actual)
    return expected == actual


def discover_expected_files() -> list:
    """Discover all expected output files organized by category"""
    files = []

    for category in CATEGORIES:
        category_dir = EXPECTED_DIR / category
        if not category_dir.exists():
            continue

        for json_file in sorted(category_dir.glob("*_expected.json")):
            test_name = json_file.stem.replace('_expected', '')
            files.append({
                "category": category,
                "test_name": test_name,
                "expected_path": json_file
            })

    return files


def compare_results(category_filter: str = None) -> dict:
    """Compare all results against expected outputs"""

    expected_files = discover_expected_files()

    if category_filter:
        expected_files = [f for f in expected_files if f["category"] == category_filter]

    if not OUTPUT_DIR.exists():
        return {"error": f"Output directory not found: {OUTPUT_DIR}"}

    total = 0
    tier1_pass = 0
    tier2_pass = 0
    overall_pass = 0
    missing = 0
    field_issues = {}
    failures = []
    by_category = {}

    for expected_file in expected_files:
        category = expected_file["category"]
        test_name = expected_file["test_name"]
        expected_path = expected_file["expected_path"]
        actual_path = OUTPUT_DIR / f"{test_name}_enriched.json"

        # Track by category
        if category not in by_category:
            by_category[category] = {
                "total": 0, "tier1_pass": 0, "tier2_pass": 0, "overall_pass": 0, "missing": 0
            }

        if not actual_path.exists():
            missing += 1
            by_category[category]["missing"] += 1
            continue

        total += 1
        by_category[category]["total"] += 1

        with open(expected_path, 'r') as f:
            expected = json.load(f)
        with open(actual_path, 'r') as f:
            actual = json.load(f)

        tier1_issues = []
        tier2_issues = []

        # Check Tier 1 fields
        for field in TIER1_FIELDS:
            exp_val = expected.get(field)
            act_val = actual.get(field)
            if not compare_value(exp_val, act_val):
                tier1_issues.append(f"{field}: exp={exp_val}, act={act_val}")
                field_issues[field] = field_issues.get(field, 0) + 1

        # Check Tier 2 fields
        for field in TIER2_FIELDS:
            exp_val = expected.get(field)
            act_val = actual.get(field)
            if not compare_value(exp_val, act_val):
                tier2_issues.append(f"{field}: exp={exp_val}, act={act_val}")
                field_issues[field] = field_issues.get(field, 0) + 1

        t1_pass = len(tier1_issues) == 0
        t2_pass = len(tier2_issues) == 0
        all_pass = t1_pass and t2_pass

        if t1_pass:
            tier1_pass += 1
            by_category[category]["tier1_pass"] += 1
        if t2_pass:
            tier2_pass += 1
            by_category[category]["tier2_pass"] += 1
        if all_pass:
            overall_pass += 1
            by_category[category]["overall_pass"] += 1
        else:
            failures.append({
                "category": category,
                "test_name": test_name,
                "tier1_issues": tier1_issues,
                "tier2_issues": tier2_issues
            })

    t1_pct = tier1_pass / total * 100 if total > 0 else 0
    t2_pct = tier2_pass / total * 100 if total > 0 else 0
    overall_pct = overall_pass / total * 100 if total > 0 else 0

    return {
        "total": total,
        "missing": missing,
        "tier1_pass": tier1_pass,
        "tier1_pct": t1_pct,
        "tier2_pass": tier2_pass,
        "tier2_pct": t2_pct,
        "overall_pass": overall_pass,
        "overall_pct": overall_pct,
        "field_issues": field_issues,
        "failures": failures,
        "by_category": by_category
    }


def print_results(result: dict, show_details: bool = False):
    """Print comparison results"""

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    print(f"\n{'='*70}")
    print(f"  V5 REGRESSION TEST RESULTS: v6.1 prompt + v6.1 schema")
    print(f"{'='*70}")

    if result["missing"] > 0:
        print(f"\n⚠️  Missing outputs: {result['missing']}")
        print(f"   Run: python run_v5_regression_test.py --all")

    t1_status = "✅" if result["tier1_pct"] >= 90 else "❌"
    t2_status = "✅" if result["tier2_pct"] >= 80 else "❌"

    print(f"\n📊 OVERALL PASS RATES (out of {result['total']} tests):")
    print(f"   Tier 1 (Critical): {result['tier1_pass']}/{result['total']} ({result['tier1_pct']:.1f}%) {t1_status} (target: ≥90%)")
    print(f"   Tier 2 (Core):     {result['tier2_pass']}/{result['total']} ({result['tier2_pct']:.1f}%) {t2_status} (target: ≥80%)")
    print(f"   Overall:           {result['overall_pass']}/{result['total']} ({result['overall_pct']:.1f}%)")

    # v5.3.4 baseline comparison
    print(f"\n📈 COMPARISON TO v5.3.4 BASELINE:")
    baseline_t1 = 93.2
    baseline_t2 = 97.7
    t1_diff = result["tier1_pct"] - baseline_t1
    t2_diff = result["tier2_pct"] - baseline_t2
    t1_indicator = "↑" if t1_diff >= 0 else "↓"
    t2_indicator = "↑" if t2_diff >= 0 else "↓"
    print(f"   Tier 1: {result['tier1_pct']:.1f}% vs 93.2% baseline ({t1_indicator}{abs(t1_diff):.1f}%)")
    print(f"   Tier 2: {result['tier2_pct']:.1f}% vs 97.7% baseline ({t2_indicator}{abs(t2_diff):.1f}%)")

    # By category breakdown
    if result["by_category"]:
        print(f"\n📊 RESULTS BY CATEGORY:")
        for cat, stats in sorted(result["by_category"].items()):
            if stats["total"] == 0:
                continue
            t1_pct = stats["tier1_pass"] / stats["total"] * 100
            t2_pct = stats["tier2_pass"] / stats["total"] * 100
            t1_icon = "✅" if t1_pct >= 90 else "❌"
            t2_icon = "✅" if t2_pct >= 80 else "❌"
            print(f"   {cat}:")
            print(f"      T1: {stats['tier1_pass']}/{stats['total']} ({t1_pct:.0f}%) {t1_icon}  T2: {stats['tier2_pass']}/{stats['total']} ({t2_pct:.0f}%) {t2_icon}")

    if result["field_issues"]:
        print(f"\n📊 ISSUES BY FIELD:")
        sorted_issues = sorted(result["field_issues"].items(), key=lambda x: -x[1])
        for field, count in sorted_issues:
            tier = "T1" if field in TIER1_FIELDS else "T2"
            print(f"   [{tier}] {field}: {count}")

    if show_details and result["failures"]:
        print(f"\n📋 DETAILED FAILURES ({len(result['failures'])} tests):")
        for f in result["failures"]:
            print(f"\n   [{f['category']}] {f['test_name']}:")
            for issue in f["tier1_issues"]:
                print(f"      [T1] {issue}")
            for issue in f["tier2_issues"]:
                print(f"      [T2] {issue}")


def main():
    parser = argparse.ArgumentParser(description="Compare v5 regression test outputs against expected")
    parser.add_argument("--details", action="store_true", help="Show detailed failures")
    parser.add_argument("--category", type=str, choices=CATEGORIES, help="Filter by category")
    args = parser.parse_args()

    result = compare_results(category_filter=args.category)
    print_results(result, show_details=args.details)


if __name__ == "__main__":
    main()
