#!/usr/bin/env python3
"""
PBH SIGNAL v6 - Test Results Comparison

Compares enriched_outputs/ vs expected_outputs/ field-by-field for all tests.
Use this after running tests to validate accuracy against the baseline.

Usage:
    python compare_results_v6.py              # Compare all tests
    python compare_results_v6.py --verbose    # Show detailed field comparisons
    python compare_results_v6.py --csv        # Generate CSV report
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class V6Comparator:
    """Compares actual vs expected test outputs for v6"""

    # TIER 1: Critical/Safety Fields (Must Pass - ≥90% Required)
    TIER1_CRITICAL_FIELDS = [
        'flags',                # adverse_event, crisis, possible_PBH_misattribution
        'relevance_label',      # Core filtering: relevant, borderline, not_relevant
        'relevance_confidence', # 0.0 to 1.0
        'bariatric_context'     # strong, weak, none
    ]

    # TIER 2: Core Product Fields (Important - ≥80% Required)
    TIER2_CORE_FIELDS = [
        'audience_label',       # patient, hcp, industry, media, unknown
        'audience_confidence',  # 0.0 to 1.0
        'sentiment_label',      # positive, negative, neutral, mixed
        'sentiment_confidence', # 0.0 to 1.0
        'themes',               # array of theme strings
        'conditions',           # array
        'treatments',           # array
        'companies',            # array
        'engagement_label',     # high, medium, low
        'engagement_score'      # integer
    ]

    # TIER 3: Enhancement Fields (Tracked, not critical)
    TIER3_ENHANCEMENT_FIELDS = [
        'emotions',             # array
        'intent',               # array
        'key_phrases',          # array
        'symptoms',             # array
        'topics',               # array
        'relevance_reason',     # string
        'debug_matches'         # array
    ]

    # Numeric fields with tolerance
    NUMERIC_FIELDS = [
        'relevance_confidence',
        'audience_confidence',
        'sentiment_confidence',
        'engagement_score'
    ]

    # Fields to skip comparison
    SKIP_FIELDS = [
        'source', 'source_id', 'url', 'permalink', 'title', 'text',
        'parent_source', 'subsource', 'author', 'country', 'published_at',
        'language', 'metrics', 'sentiment_raw'
    ]

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.results = []

    def calculate_overlap_score(self, expected: List, actual: List) -> float:
        """Calculate Jaccard similarity for list fields"""
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0

        expected_set = set(expected)
        actual_set = set(actual)
        intersection = len(expected_set & actual_set)
        union = len(expected_set | actual_set)

        return intersection / union if union > 0 else 0.0

    def compare_arrays(self, expected: List, actual: List) -> Tuple[bool, float, str]:
        """Compare two arrays. Returns: (exact_match, overlap_ratio, details)"""
        if not expected and not actual:
            return True, 1.0, "Both empty"

        if not expected or not actual:
            return False, 0.0, f"Expected: {expected}, Actual: {actual}"

        expected_set = set(expected) if expected else set()
        actual_set = set(actual) if actual else set()

        if expected_set == actual_set:
            return True, 1.0, "Exact match"

        overlap = self.calculate_overlap_score(expected, actual)
        missing = expected_set - actual_set
        extra = actual_set - expected_set

        details = []
        if missing:
            details.append(f"Missing: {sorted(missing)}")
        if extra:
            details.append(f"Extra: {sorted(extra)}")

        return False, overlap, "; ".join(details)

    def compare_values(self, expected: Any, actual: Any, field_name: str) -> Tuple[bool, str]:
        """Compare two values. Returns: (match, details)"""
        if expected == actual:
            return True, "Match"

        # Numeric tolerance
        if field_name in self.NUMERIC_FIELDS:
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                diff = abs(expected - actual)
                if diff <= 0.15:  # Allow 0.15 tolerance for confidence scores
                    return True, f"Close match (diff: {diff:.3f})"
                return False, f"Mismatch (expected: {expected}, actual: {actual}, diff: {diff:.3f})"

        return False, f"Expected: {expected}, Actual: {actual}"

    def compare_test(self, expected_path: Path, actual_path: Path) -> Dict:
        """Compare a single test's expected vs actual output"""

        source_id = expected_path.stem.replace('_enriched', '')

        with open(expected_path, 'r') as f:
            expected = json.load(f)

        with open(actual_path, 'r') as f:
            actual = json.load(f)

        result = {
            'source_id': source_id,
            'overall_pass': True,
            'tier1_pass': True,
            'tier2_pass': True,
            'tier3_pass': True,
            'tier1_score': 0.0,
            'tier2_score': 0.0,
            'tier3_score': 0.0,
            'field_results': {},
            'mismatches': []
        }

        tier1_scores = []
        tier2_scores = []
        tier3_scores = []

        # Compare each field
        all_fields = set(expected.keys()).union(set(actual.keys()))

        for field in all_fields:
            if field in self.SKIP_FIELDS:
                continue

            expected_val = expected.get(field)
            actual_val = actual.get(field)

            # Handle arrays
            if isinstance(expected_val, list) or isinstance(actual_val, list):
                expected_list = expected_val if isinstance(expected_val, list) else []
                actual_list = actual_val if isinstance(actual_val, list) else []

                exact_match, overlap, details = self.compare_arrays(expected_list, actual_list)

                field_result = {
                    'match': exact_match,
                    'overlap': overlap,
                    'expected': expected_val,
                    'actual': actual_val,
                    'details': details
                }

                if field in self.TIER1_CRITICAL_FIELDS:
                    tier1_scores.append(1.0 if exact_match else overlap)
                    if not exact_match:
                        result['tier1_pass'] = False
                        result['overall_pass'] = False
                        result['mismatches'].append(f"[T1] {field}: {details}")

                elif field in self.TIER2_CORE_FIELDS:
                    tier2_scores.append(1.0 if exact_match else overlap)
                    if overlap < 0.8:
                        result['tier2_pass'] = False
                        result['overall_pass'] = False
                        result['mismatches'].append(f"[T2] {field}: {details}")

                elif field in self.TIER3_ENHANCEMENT_FIELDS:
                    tier3_scores.append(1.0 if exact_match else overlap)
                    # Tier 3 doesn't affect overall pass

                result['field_results'][field] = field_result

            # Handle simple values
            else:
                match, details = self.compare_values(expected_val, actual_val, field)

                field_result = {
                    'match': match,
                    'expected': expected_val,
                    'actual': actual_val,
                    'details': details
                }

                if field in self.TIER1_CRITICAL_FIELDS:
                    tier1_scores.append(1.0 if match else 0.0)
                    if not match:
                        result['tier1_pass'] = False
                        result['overall_pass'] = False
                        result['mismatches'].append(f"[T1] {field}: {details}")

                elif field in self.TIER2_CORE_FIELDS:
                    tier2_scores.append(1.0 if match else 0.0)
                    if not match:
                        result['tier2_pass'] = False
                        result['overall_pass'] = False
                        result['mismatches'].append(f"[T2] {field}: {details}")

                elif field in self.TIER3_ENHANCEMENT_FIELDS:
                    tier3_scores.append(1.0 if match else 0.0)

                result['field_results'][field] = field_result

        # Calculate tier scores
        result['tier1_score'] = sum(tier1_scores) / len(tier1_scores) if tier1_scores else 1.0
        result['tier2_score'] = sum(tier2_scores) / len(tier2_scores) if tier2_scores else 1.0
        result['tier3_score'] = sum(tier3_scores) / len(tier3_scores) if tier3_scores else 1.0

        return result

    def run_comparison(self, verbose: bool = False) -> List[Dict]:
        """Run comparison for all tests"""

        expected_dir = self.base_dir / "expected_outputs"
        actual_dir = self.base_dir / "enriched_outputs"

        if not expected_dir.exists():
            print(f"❌ Error: expected_outputs directory not found")
            return []

        if not actual_dir.exists():
            print(f"❌ Error: enriched_outputs directory not found")
            return []

        expected_files = sorted(expected_dir.glob("*_enriched.json"))

        if not expected_files:
            print(f"❌ Error: No expected output files found")
            return []

        print(f"\n🔍 Comparing {len(expected_files)} test results...\n")

        tier1_pass_count = 0
        tier2_pass_count = 0
        overall_pass_count = 0
        missing_count = 0

        for expected_path in expected_files:
            source_id = expected_path.stem.replace('_enriched', '')
            actual_path = actual_dir / expected_path.name

            if not actual_path.exists():
                print(f"❌ {source_id}: Missing actual output")
                missing_count += 1
                continue

            result = self.compare_test(expected_path, actual_path)
            self.results.append(result)

            if result['overall_pass']:
                status = "✅"
                overall_pass_count += 1
            elif result['tier1_pass']:
                status = "⚠️ "
            else:
                status = "❌"

            if result['tier1_pass']:
                tier1_pass_count += 1
            if result['tier2_pass']:
                tier2_pass_count += 1

            if verbose:
                print(f"{status} {source_id}")
                print(f"     Tier 1: {result['tier1_score']*100:.0f}% | Tier 2: {result['tier2_score']*100:.0f}% | Tier 3: {result['tier3_score']*100:.0f}%")
                if result['mismatches']:
                    for mismatch in result['mismatches']:
                        print(f"     • {mismatch}")
                print()
            else:
                t1 = "✓" if result['tier1_pass'] else "✗"
                t2 = "✓" if result['tier2_pass'] else "✗"
                print(f"{status} {source_id}: T1={t1} T2={t2}")

        return self.results

    def print_summary(self):
        """Print summary statistics"""

        if not self.results:
            return

        total = len(self.results)

        tier1_pass = sum(1 for r in self.results if r['tier1_pass'])
        tier2_pass = sum(1 for r in self.results if r['tier2_pass'])
        overall_pass = sum(1 for r in self.results if r['overall_pass'])

        avg_tier1 = sum(r['tier1_score'] for r in self.results) / total * 100
        avg_tier2 = sum(r['tier2_score'] for r in self.results) / total * 100
        avg_tier3 = sum(r['tier3_score'] for r in self.results) / total * 100

        print()
        print("=" * 70)
        print("v6 COMPARISON SUMMARY")
        print("=" * 70)
        print()

        print("📊 TIER PASS RATES:")
        print(f"   Tier 1 (Critical/Safety): {tier1_pass}/{total} ({tier1_pass/total*100:.1f}%) - Target ≥90%")
        print(f"   Tier 2 (Core Product):    {tier2_pass}/{total} ({tier2_pass/total*100:.1f}%) - Target ≥80%")
        print(f"   Overall (Tier 1 + 2):     {overall_pass}/{total} ({overall_pass/total*100:.1f}%)")
        print()

        print("📊 AVERAGE SCORES:")
        print(f"   Tier 1: {avg_tier1:.1f}%")
        print(f"   Tier 2: {avg_tier2:.1f}%")
        print(f"   Tier 3: {avg_tier3:.1f}% (Enhancement - tracked only)")
        print()

        # Collect all mismatches by field
        field_mismatches = {}
        for r in self.results:
            for mismatch in r['mismatches']:
                # Extract field name from mismatch string
                field = mismatch.split(']')[1].split(':')[0].strip() if ']' in mismatch else 'unknown'
                if field not in field_mismatches:
                    field_mismatches[field] = []
                field_mismatches[field].append(r['source_id'])

        if field_mismatches:
            print("📊 MISMATCHES BY FIELD:")
            for field, source_ids in sorted(field_mismatches.items(), key=lambda x: -len(x[1])):
                print(f"   {field}: {len(source_ids)} test(s)")
                for sid in source_ids[:3]:  # Show first 3
                    print(f"      - {sid}")
                if len(source_ids) > 3:
                    print(f"      ... and {len(source_ids) - 3} more")
            print()

        # Pass/fail determination
        tier1_pct = tier1_pass / total * 100
        tier2_pct = tier2_pass / total * 100

        if tier1_pct >= 90 and tier2_pct >= 80:
            print("🎉 v6 VALIDATION: PASSED")
        elif tier1_pct >= 90:
            print("⚠️  v6 VALIDATION: PARTIAL (Tier 1 OK, Tier 2 needs work)")
        else:
            print("❌ v6 VALIDATION: NEEDS WORK (Tier 1 < 90%)")

        print("=" * 70)

    def generate_csv(self, output_path: Path = None):
        """Generate CSV report"""

        if not self.results:
            return

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = self.base_dir / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            output_path = reports_dir / f"v6_comparison_{timestamp}.csv"

        fieldnames = [
            'source_id',
            'overall_pass',
            'tier1_pass',
            'tier2_pass',
            'tier1_score',
            'tier2_score',
            'tier3_score',
            'relevance_match',
            'bariatric_context_match',
            'flags_match',
            'audience_match',
            'sentiment_match',
            'themes_match',
            'mismatches'
        ]

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                fr = result['field_results']

                row = {
                    'source_id': result['source_id'],
                    'overall_pass': 'PASS' if result['overall_pass'] else 'FAIL',
                    'tier1_pass': 'PASS' if result['tier1_pass'] else 'FAIL',
                    'tier2_pass': 'PASS' if result['tier2_pass'] else 'FAIL',
                    'tier1_score': f"{result['tier1_score']:.2f}",
                    'tier2_score': f"{result['tier2_score']:.2f}",
                    'tier3_score': f"{result['tier3_score']:.2f}",
                    'relevance_match': 'PASS' if fr.get('relevance_label', {}).get('match', True) else 'FAIL',
                    'bariatric_context_match': 'PASS' if fr.get('bariatric_context', {}).get('match', True) else 'FAIL',
                    'flags_match': 'PASS' if fr.get('flags', {}).get('match', True) else 'FAIL',
                    'audience_match': 'PASS' if fr.get('audience_label', {}).get('match', True) else 'FAIL',
                    'sentiment_match': 'PASS' if fr.get('sentiment_label', {}).get('match', True) else 'FAIL',
                    'themes_match': 'PASS' if fr.get('themes', {}).get('match', True) else 'FAIL',
                    'mismatches': '; '.join(result['mismatches']) if result['mismatches'] else ''
                }

                writer.writerow(row)

        print(f"\n📄 CSV report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare v6 test results against expected outputs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed per-test results")
    parser.add_argument("--csv", action="store_true", help="Generate CSV report")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    comparator = V6Comparator(base_dir)

    comparator.run_comparison(verbose=args.verbose)
    comparator.print_summary()

    if args.csv:
        comparator.generate_csv()


if __name__ == "__main__":
    main()
