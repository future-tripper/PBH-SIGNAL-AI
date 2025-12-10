#!/usr/bin/env python3
"""
Compare v7 API test outputs against expected outputs.

Usage:
    python compare_v7.py              # Compare v7 results
    python compare_v7.py --details    # Show detailed failures
"""

import argparse
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent
EXPECTED_DIR = BASE_DIR / "expected_outputs"
OUTPUT_DIR = BASE_DIR / "api_test_outputs" / "v7"

# TIER 1: Critical/Safety Fields
TIER1_FIELDS = ['flags', 'relevance_label', 'bariatric_context']

# TIER 2: Core Product Fields
TIER2_FIELDS = ['audience_label', 'sentiment_label', 'themes', 'conditions',
                'treatments', 'companies', 'symptoms', 'topics', 'engagement_label', 'emotions']


def compare_value(expected: Any, actual: Any) -> bool:
    """Compare two values (set comparison for lists)"""
    if isinstance(expected, list) and isinstance(actual, list):
        return set(expected) == set(actual)
    return expected == actual


def compare_v7() -> dict:
    """Compare v7 results against expected outputs"""

    if not OUTPUT_DIR.exists():
        return {"error": f"Output directory not found: {OUTPUT_DIR}"}

    expected_files = sorted(EXPECTED_DIR.glob("*_enriched.json"))

    total = 0
    tier1_pass = 0
    tier2_pass = 0
    overall_pass = 0
    missing = 0
    field_issues = {}
    failures = []

    for expected_path in expected_files:
        source_id = expected_path.stem.replace('_enriched', '')
        actual_path = OUTPUT_DIR / expected_path.name

        if not actual_path.exists():
            missing += 1
            continue

        total += 1

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
        if t2_pass:
            tier2_pass += 1
        if all_pass:
            overall_pass += 1
        else:
            failures.append({
                "source_id": source_id,
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
        "failures": failures
    }


def print_result(result: dict, show_details: bool = False):
    """Print comparison result"""

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    print(f"\n{'='*70}")
    print(f"  v7 COMPARISON RESULTS")
    print(f"{'='*70}")

    if result["missing"] > 0:
        print(f"\n⚠️  Missing outputs: {result['missing']}")

    t1_status = "✅" if result["tier1_pct"] >= 90 else "❌"
    t2_status = "✅" if result["tier2_pct"] >= 80 else "❌"

    print(f"\n📊 PASS RATES (out of {result['total']} tests):")
    print(f"   Tier 1 (Critical): {result['tier1_pass']}/{result['total']} ({result['tier1_pct']:.1f}%) {t1_status} (target ≥90%)")
    print(f"   Tier 2 (Core):     {result['tier2_pass']}/{result['total']} ({result['tier2_pct']:.1f}%) {t2_status} (target ≥80%)")
    print(f"   Overall:           {result['overall_pass']}/{result['total']} ({result['overall_pct']:.1f}%)")

    if result["field_issues"]:
        print(f"\n📊 ISSUES BY FIELD:")
        sorted_issues = sorted(result["field_issues"].items(), key=lambda x: -x[1])
        for field, count in sorted_issues:
            tier = "T1" if field in TIER1_FIELDS else "T2"
            print(f"   [{tier}] {field}: {count}")

    if show_details and result["failures"]:
        print(f"\n📋 DETAILED FAILURES ({len(result['failures'])} cases):")
        for f in result["failures"]:
            print(f"\n   {f['source_id']}:")
            for issue in f["tier1_issues"]:
                print(f"      [T1] {issue}")
            for issue in f["tier2_issues"]:
                print(f"      [T2] {issue}")


def main():
    parser = argparse.ArgumentParser(description="Compare v7 API test outputs against expected")
    parser.add_argument("--details", action="store_true", help="Show detailed failures")
    args = parser.parse_args()

    result = compare_v7()
    print_result(result, show_details=args.details)


if __name__ == "__main__":
    main()
