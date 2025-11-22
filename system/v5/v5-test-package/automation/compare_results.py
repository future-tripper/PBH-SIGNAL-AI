#!/usr/bin/env python3
"""
PBH SIGNAL v5 - Test Results Comparison

Compares actual vs expected outputs field-by-field for all tests.
Generates detailed comparison report and CSV results.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Any


class TestComparator:
    """Compares actual vs expected test outputs"""

    # TIER 1: Critical/Safety Fields (Must Pass - 90%+ Required)
    # These are essential for patient safety and core product functionality
    TIER1_CRITICAL_FIELDS = [
        'flags',                # adverse_event, crisis flags
        'relevance_label',      # Core filtering
        'audience_label',       # Who's posting
        'bariatric_context'     # Context detection
    ]

    # TIER 2: Core Product Fields (Important - 80%+ Required)
    # These enhance product quality and user experience
    TIER2_CORE_FIELDS = [
        'sentiment_label',
        'engagement_label'
    ]

    # TIER 3: Enhancement Fields (Nice-to-Have - Track Only)
    # These are subjective and provide additional insights but aren't critical
    TIER3_ENHANCEMENT_FIELDS = [
        'themes',
        'emotions',
        'intent'
    ]

    # Entity extraction fields (high overlap ≥0.8 expected)
    ENTITY_FIELDS = [
        'topics',
        'symptoms',
        'treatments',
        'conditions',
        'companies',
        'debug_matches'
    ]

    # Confidence/score fields (exact match not expected, ±0.1 tolerance)
    NUMERIC_FIELDS = [
        'relevance_confidence',
        'audience_confidence',
        'sentiment_confidence',
        'engagement_score'
    ]

    # Legacy: Keep for backward compatibility
    CRITICAL_FIELDS = TIER1_CRITICAL_FIELDS  # Alias
    CLASSIFICATION_FIELDS = TIER2_CORE_FIELDS + TIER3_ENHANCEMENT_FIELDS  # Combined

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.results = []

    def compare_arrays(self, expected: List, actual: List) -> Tuple[bool, float, str]:
        """
        Compare two arrays.
        Returns: (exact_match, overlap_ratio, details)
        """
        if not expected and not actual:
            return True, 1.0, "Both empty"

        if not expected or not actual:
            return False, 0.0, f"Expected: {expected}, Actual: {actual}"

        expected_set = set(expected)
        actual_set = set(actual)

        if expected_set == actual_set:
            return True, 1.0, "Exact match"

        intersection = expected_set.intersection(actual_set)
        union = expected_set.union(actual_set)
        overlap = len(intersection) / len(union) if union else 0.0

        missing = expected_set - actual_set
        extra = actual_set - expected_set

        details = []
        if missing:
            details.append(f"Missing: {sorted(missing)}")
        if extra:
            details.append(f"Extra: {sorted(extra)}")

        return False, overlap, "; ".join(details)

    def compare_values(self, expected: Any, actual: Any, field_name: str) -> Tuple[bool, str]:
        """
        Compare two values.
        Returns: (match, details)
        """
        if expected == actual:
            return True, "Match"

        # For numeric fields, allow small variance
        if field_name in self.NUMERIC_FIELDS:
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                diff = abs(expected - actual)
                if diff <= 0.1:
                    return True, f"Close match (diff: {diff:.3f})"
                return False, f"Mismatch (expected: {expected}, actual: {actual}, diff: {diff:.3f})"

        return False, f"Expected: {expected}, Actual: {actual}"

    def compare_test(self, expected_path: Path, actual_path: Path) -> Dict:
        """Compare a single test's expected vs actual output"""

        test_name = expected_path.stem.replace('_expected', '')

        # Load files
        with open(expected_path, 'r') as f:
            expected = json.load(f)

        with open(actual_path, 'r') as f:
            actual = json.load(f)

        result = {
            'test_name': test_name,
            'overall_pass': True,
            'critical_pass': True,  # Legacy: same as tier1_pass
            'tier1_pass': True,     # Tier 1: Critical/Safety fields
            'tier2_pass': True,     # Tier 2: Core product fields
            'tier3_pass': True,     # Tier 3: Enhancement fields
            'field_results': {}
        }

        # Compare each field
        all_fields = set(expected.keys()).union(set(actual.keys()))

        for field in all_fields:
            expected_val = expected.get(field)
            actual_val = actual.get(field)

            # Skip author object (not enriched)
            if field == 'author':
                continue

            # Handle arrays
            if isinstance(expected_val, list) and isinstance(actual_val, list):
                exact_match, overlap, details = self.compare_arrays(expected_val, actual_val)

                field_result = {
                    'match': exact_match,
                    'overlap': overlap,
                    'details': details
                }

                # For tier 1 (critical) fields, require exact match
                if field in self.TIER1_CRITICAL_FIELDS:
                    if not exact_match:
                        result['overall_pass'] = False
                        result['critical_pass'] = False
                        result['tier1_pass'] = False

                # For tier 2 (core) fields, require exact match
                elif field in self.TIER2_CORE_FIELDS:
                    if not exact_match:
                        result['overall_pass'] = False
                        result['tier2_pass'] = False

                # For tier 3 (enhancement) fields, require exact match
                elif field in self.TIER3_ENHANCEMENT_FIELDS:
                    if not exact_match:
                        result['overall_pass'] = False
                        result['tier3_pass'] = False

                # For entity fields, allow high overlap (>= 0.8)
                elif field in self.ENTITY_FIELDS:
                    if overlap < 0.8:
                        result['overall_pass'] = False

                result['field_results'][field] = field_result

            # Handle nested objects (like metrics)
            elif isinstance(expected_val, dict) and isinstance(actual_val, dict):
                # Simple nested comparison
                nested_match = expected_val == actual_val
                result['field_results'][field] = {
                    'match': nested_match,
                    'details': 'Match' if nested_match else f'Mismatch'
                }
                if not nested_match and field not in ['metrics']:
                    result['overall_pass'] = False

            # Handle simple values
            else:
                match, details = self.compare_values(expected_val, actual_val, field)
                result['field_results'][field] = {
                    'match': match,
                    'details': details
                }

                if not match:
                    if field in self.TIER1_CRITICAL_FIELDS:
                        result['overall_pass'] = False
                        result['critical_pass'] = False
                        result['tier1_pass'] = False
                    elif field in self.TIER2_CORE_FIELDS:
                        result['overall_pass'] = False
                        result['tier2_pass'] = False
                    elif field in self.TIER3_ENHANCEMENT_FIELDS:
                        result['overall_pass'] = False
                        result['tier3_pass'] = False

        return result

    def run_comparison(self):
        """Run comparison for all tests"""

        # Find all expected output files
        expected_base = self.base_dir.parent.parent / "enrichment-test-data-v5" / "expected-outputs"

        test_dirs = [
            "ae-test-cases",
            "platform-coverage",
            "edge-cases",
            "dictionary-tests",
            "classification-tests",
            "flag-tests"
        ]

        expected_files = []
        for test_dir in test_dirs:
            dir_path = expected_base / test_dir
            if dir_path.exists():
                expected_files.extend(sorted(dir_path.glob("*_expected.json")))

        actual_dir = self.base_dir.parent / "actual_outputs"

        print(f"🔍 Comparing {len(expected_files)} test results...\n")

        total_pass = 0
        total_fail = 0
        critical_failures = []

        for expected_path in expected_files:
            test_name = expected_path.stem.replace('_expected', '')
            actual_path = actual_dir / f"{test_name}_actual.json"

            if not actual_path.exists():
                print(f"❌ {test_name}: Missing actual output")
                total_fail += 1
                continue

            result = self.compare_test(expected_path, actual_path)
            self.results.append(result)

            if result['overall_pass']:
                print(f"✅ {test_name}")
                total_pass += 1
            else:
                status = "❌ CRITICAL" if not result['critical_pass'] else "⚠️  Minor"
                print(f"{status} {test_name}")
                total_fail += 1

                if not result['critical_pass']:
                    critical_failures.append(test_name)

                # Show failed fields
                for field, field_result in result['field_results'].items():
                    if not field_result.get('match', False):
                        overlap = field_result.get('overlap', 0.0)
                        if field in self.ENTITY_FIELDS and overlap >= 0.8:
                            continue  # Don't show high-overlap entity mismatches
                        details = field_result.get('details', '')
                        print(f"     • {field}: {details}")

        print()
        print("=" * 70)
        print(f"Comparison Summary:")
        print(f"  Total tests: {len(expected_files)}")
        print(f"  Passed: {total_pass}")
        print(f"  Failed: {total_fail}")
        print(f"  Success rate: {total_pass / len(expected_files) * 100:.1f}%")

        if critical_failures:
            print(f"\n⚠️  Critical failures ({len(critical_failures)}):")
            for test in critical_failures:
                print(f"     • {test}")

        print("=" * 70)

    def generate_csv(self, output_path: Path):
        """Generate phase1_test_results.csv"""

        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'test_name',
                'category',
                'tier1_pass',           # NEW: Tier 1 (Critical/Safety) pass
                'tier2_pass',           # NEW: Tier 2 (Core Product) pass
                'tier3_pass',           # NEW: Tier 3 (Enhancement) pass
                'overall_pass',         # Legacy: all fields
                'critical_pass',        # Legacy: same as tier1_pass
                'flags_match',
                'relevance_match',
                'audience_match',
                'bariatric_context_match',
                'sentiment_match',
                'themes_match',
                'entity_extraction_quality',
                'notes'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                test_name = result['test_name']

                # Determine category from test name
                if test_name.startswith('ae_test'):
                    category = 'adverse_events'
                elif test_name.startswith('platform_'):
                    category = 'platform_coverage'
                elif test_name.startswith('edge_'):
                    category = 'edge_cases'
                elif test_name.startswith('dict_'):
                    category = 'dictionary'
                elif test_name.startswith('class_'):
                    category = 'classification'
                elif test_name.startswith('flag_'):
                    category = 'flags'
                else:
                    category = 'unknown'

                field_results = result['field_results']

                # Check entity extraction quality
                entity_overlaps = []
                for field in self.ENTITY_FIELDS:
                    if field in field_results:
                        overlap = field_results[field].get('overlap', 1.0)
                        entity_overlaps.append(overlap)

                avg_entity_overlap = sum(entity_overlaps) / len(entity_overlaps) if entity_overlaps else 1.0

                # Collect notes for failures
                notes = []
                for field, field_result in field_results.items():
                    if not field_result.get('match', False):
                        if field in self.CRITICAL_FIELDS or field in self.CLASSIFICATION_FIELDS:
                            notes.append(f"{field}: {field_result.get('details', 'mismatch')}")

                row = {
                    'test_name': test_name,
                    'category': category,
                    'tier1_pass': 'PASS' if result['tier1_pass'] else 'FAIL',
                    'tier2_pass': 'PASS' if result['tier2_pass'] else 'FAIL',
                    'tier3_pass': 'PASS' if result['tier3_pass'] else 'FAIL',
                    'overall_pass': 'PASS' if result['overall_pass'] else 'FAIL',
                    'critical_pass': 'PASS' if result['critical_pass'] else 'FAIL',
                    'flags_match': 'PASS' if field_results.get('flags', {}).get('match', True) else 'FAIL',
                    'relevance_match': 'PASS' if field_results.get('relevance_label', {}).get('match', True) else 'FAIL',
                    'audience_match': 'PASS' if field_results.get('audience_label', {}).get('match', True) else 'FAIL',
                    'bariatric_context_match': 'PASS' if field_results.get('bariatric_context', {}).get('match', True) else 'FAIL',
                    'sentiment_match': 'PASS' if field_results.get('sentiment_label', {}).get('match', True) else 'FAIL',
                    'themes_match': 'PASS' if field_results.get('themes', {}).get('match', True) else 'FAIL',
                    'entity_extraction_quality': f"{avg_entity_overlap:.2f}",
                    'notes': '; '.join(notes) if notes else 'All fields match'
                }

                writer.writerow(row)

        print(f"\n✅ CSV report saved to: {output_path}")


def main():
    base_dir = Path(__file__).parent
    comparator = TestComparator(base_dir)

    comparator.run_comparison()

    csv_path = base_dir.parent / "phase1_test_results.csv"
    comparator.generate_csv(csv_path)


if __name__ == "__main__":
    main()
