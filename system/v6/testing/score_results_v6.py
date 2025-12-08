#!/usr/bin/env python3
"""
PBH SIGNAL v6 - Test Results Scoring

Compares enriched outputs against expected outcomes from v6_expected_outcomes.json.
Focuses on relevance_label accuracy (primary v6 goal) and key field validation.

Usage:
    python score_results_v6.py                # Score all results
    python score_results_v6.py --verbose      # Show detailed per-test results
    python score_results_v6.py --csv          # Generate CSV report
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class V6Scorer:
    """Score v6 test results against expected outcomes"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.expected_outcomes = None
        self.results = []

    def load_expected_outcomes(self):
        """Load expected outcomes manifest"""
        manifest_path = self.base_dir / "v6_expected_outcomes.json"
        if not manifest_path.exists():
            print(f"❌ Error: Expected outcomes manifest not found")
            print(f"   Run generate_expected_outcomes.py first")
            return False

        with open(manifest_path, 'r') as f:
            self.expected_outcomes = json.load(f)

        print(f"✅ Loaded expected outcomes for {self.expected_outcomes['total_tests']} tests")
        return True

    def score_single_test(self, source_id: str, enriched: dict, expected: dict) -> dict:
        """
        Score a single test result.

        Returns dict with:
        - source_id
        - relevance_match: bool
        - bariatric_context_match: bool
        - bariatric_context_populated: bool
        - treatments_found: list
        - expected_treatments: list
        - treatments_match: bool
        - overall_pass: bool
        - details: dict with specifics
        """
        result = {
            "source_id": source_id,
            "test_category": expected.get("test_category", "unknown"),
            "v6_rule": expected.get("v6_rule", ""),

            # Expected values
            "expected_relevance": expected.get("expected_relevance_label"),
            "expected_bariatric_context": expected.get("expected_bariatric_context"),
            "expected_treatments": expected.get("expected_treatments", []),

            # Actual values
            "actual_relevance": enriched.get("relevance_label"),
            "actual_bariatric_context": enriched.get("bariatric_context"),
            "actual_treatments": enriched.get("treatments", []),

            # Scores
            "relevance_match": False,
            "bariatric_context_match": False,
            "bariatric_context_populated": False,
            "treatments_match": False,
            "overall_pass": False,

            # Details
            "relevance_reason": enriched.get("relevance_reason", ""),
            "notes": []
        }

        # Check relevance_label match (PRIMARY METRIC)
        if result["actual_relevance"] == result["expected_relevance"]:
            result["relevance_match"] = True
        else:
            result["notes"].append(
                f"Relevance mismatch: expected {result['expected_relevance']}, got {result['actual_relevance']}"
            )

        # Check bariatric_context populated (must not be empty/None)
        if result["actual_bariatric_context"] in ["strong", "weak", "none"]:
            result["bariatric_context_populated"] = True
        else:
            result["notes"].append(f"bariatric_context not populated: {result['actual_bariatric_context']}")

        # Check bariatric_context match
        if result["actual_bariatric_context"] == result["expected_bariatric_context"]:
            result["bariatric_context_match"] = True
        else:
            # Allow some flexibility - "weak" vs "strong" is less critical than "none"
            if result["expected_bariatric_context"] != "none" and result["actual_bariatric_context"] != "none":
                result["notes"].append(
                    f"bariatric_context differs: expected {result['expected_bariatric_context']}, got {result['actual_bariatric_context']} (partial credit)"
                )
            else:
                result["notes"].append(
                    f"bariatric_context mismatch: expected {result['expected_bariatric_context']}, got {result['actual_bariatric_context']}"
                )

        # Check treatments extraction
        expected_treatments = set(result["expected_treatments"])
        actual_treatments = set(result["actual_treatments"])

        if expected_treatments:
            found = expected_treatments.intersection(actual_treatments)
            missing = expected_treatments - actual_treatments
            if missing:
                result["notes"].append(f"Missing treatments: {list(missing)}")
            if found == expected_treatments:
                result["treatments_match"] = True
        else:
            # No expected treatments, so match if we didn't find any PBH treatments
            pbh_treatments = {"avexitide", "acarbose", "diazoxide", "octreotide"}
            unexpected_pbh = actual_treatments.intersection(pbh_treatments)
            if not unexpected_pbh:
                result["treatments_match"] = True
            else:
                result["notes"].append(f"Unexpected PBH treatments found: {list(unexpected_pbh)}")

        # Overall pass: relevance must match, and bariatric_context must be populated
        result["overall_pass"] = (
            result["relevance_match"] and
            result["bariatric_context_populated"]
        )

        return result

    def run_scoring(self, verbose: bool = False) -> List[dict]:
        """Run scoring for all test results"""

        if not self.expected_outcomes:
            return []

        # Build lookup of expected outcomes by source_id
        expected_by_id = {
            p["source_id"]: p for p in self.expected_outcomes["test_posts"]
        }

        # Find enriched output files
        output_dir = self.base_dir / "enriched_outputs"
        if not output_dir.exists():
            print(f"❌ Error: enriched_outputs directory not found")
            print(f"   Run run_tests_v6.py first")
            return []

        enriched_files = sorted(output_dir.glob("*_enriched.json"))

        if not enriched_files:
            print(f"❌ Error: No enriched output files found")
            return []

        print(f"\n🔍 Scoring {len(enriched_files)} test results...\n")

        # Score each test
        for enriched_file in enriched_files:
            source_id = enriched_file.stem.replace("_enriched", "")

            # Load enriched output
            with open(enriched_file, 'r') as f:
                enriched = json.load(f)

            # Find expected outcome
            expected = expected_by_id.get(source_id)
            if not expected:
                print(f"⚠️  {source_id}: No expected outcome found (skipping)")
                continue

            # Score
            result = self.score_single_test(source_id, enriched, expected)
            self.results.append(result)

            # Print result
            if result["overall_pass"]:
                status = "✅"
            elif result["relevance_match"]:
                status = "⚠️ "  # Relevance correct but other issues
            else:
                status = "❌"

            if verbose:
                print(f"{status} {source_id}")
                print(f"     Category: {result['test_category']}")
                print(f"     Relevance: {result['actual_relevance']} (expected: {result['expected_relevance']})")
                print(f"     Context: {result['actual_bariatric_context']} (expected: {result['expected_bariatric_context']})")
                if result["notes"]:
                    for note in result["notes"]:
                        print(f"     ⚠️  {note}")
                print()
            else:
                rel_status = "✓" if result["relevance_match"] else "✗"
                ctx_status = "✓" if result["bariatric_context_match"] else "~" if result["bariatric_context_populated"] else "✗"
                print(f"{status} {source_id}: rel={rel_status} ctx={ctx_status} ({result['test_category']})")

        return self.results

    def print_summary(self):
        """Print summary statistics"""

        if not self.results:
            return

        total = len(self.results)

        # Primary metric: relevance_label accuracy
        relevance_correct = sum(1 for r in self.results if r["relevance_match"])

        # Secondary metrics
        context_populated = sum(1 for r in self.results if r["bariatric_context_populated"])
        context_match = sum(1 for r in self.results if r["bariatric_context_match"])
        treatments_match = sum(1 for r in self.results if r["treatments_match"])
        overall_pass = sum(1 for r in self.results if r["overall_pass"])

        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r["test_category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "relevance_pass": 0, "overall_pass": 0}
            categories[cat]["total"] += 1
            if r["relevance_match"]:
                categories[cat]["relevance_pass"] += 1
            if r["overall_pass"]:
                categories[cat]["overall_pass"] += 1

        # Relevance confusion matrix
        relevance_matrix = {
            "relevant_correct": 0,
            "relevant_as_borderline": 0,
            "relevant_as_not_relevant": 0,
            "borderline_correct": 0,
            "borderline_as_relevant": 0,
            "borderline_as_not_relevant": 0,
            "not_relevant_correct": 0,
            "not_relevant_as_relevant": 0,
            "not_relevant_as_borderline": 0
        }

        for r in self.results:
            exp = r["expected_relevance"]
            act = r["actual_relevance"]
            if exp == act:
                relevance_matrix[f"{exp}_correct"] += 1
            else:
                relevance_matrix[f"{exp}_as_{act}"] += 1

        print()
        print("=" * 70)
        print("v6 TEST RESULTS SUMMARY")
        print("=" * 70)
        print()

        # Primary metric
        print("📊 PRIMARY METRIC: Relevance Label Accuracy")
        print(f"   ✅ Correct: {relevance_correct}/{total} ({relevance_correct/total*100:.1f}%)")
        print(f"   ❌ Wrong: {total - relevance_correct}/{total} ({(total-relevance_correct)/total*100:.1f}%)")
        print()

        # Relevance breakdown
        print("📋 Relevance Confusion Matrix:")
        for exp in ["relevant", "borderline", "not_relevant"]:
            correct = relevance_matrix[f"{exp}_correct"]
            exp_total = sum(1 for r in self.results if r["expected_relevance"] == exp)
            if exp_total > 0:
                print(f"   {exp} ({exp_total} expected):")
                print(f"      ✓ Correct: {correct}")
                for other in ["relevant", "borderline", "not_relevant"]:
                    if other != exp:
                        wrong = relevance_matrix.get(f"{exp}_as_{other}", 0)
                        if wrong > 0:
                            print(f"      ✗ As {other}: {wrong}")
        print()

        # Secondary metrics
        print("📊 SECONDARY METRICS:")
        print(f"   bariatric_context populated: {context_populated}/{total} ({context_populated/total*100:.1f}%)")
        print(f"   bariatric_context exact match: {context_match}/{total} ({context_match/total*100:.1f}%)")
        print(f"   treatments extraction: {treatments_match}/{total} ({treatments_match/total*100:.1f}%)")
        print()

        # Category breakdown
        print("📊 BY CATEGORY:")
        for cat, stats in sorted(categories.items(), key=lambda x: -x[1]["total"]):
            rel_pct = stats["relevance_pass"] / stats["total"] * 100
            overall_pct = stats["overall_pass"] / stats["total"] * 100
            print(f"   {cat} ({stats['total']} tests):")
            print(f"      Relevance: {stats['relevance_pass']}/{stats['total']} ({rel_pct:.0f}%)")
            print(f"      Overall: {stats['overall_pass']}/{stats['total']} ({overall_pct:.0f}%)")
        print()

        # Overall
        print("📊 OVERALL PASS (relevance correct + context populated):")
        print(f"   {overall_pass}/{total} ({overall_pass/total*100:.1f}%)")
        print()

        # Pass/Fail determination
        relevance_pct = relevance_correct / total * 100
        if relevance_pct >= 95:
            print("🎉 v6 VALIDATION: PASSED (≥95% relevance accuracy)")
        elif relevance_pct >= 90:
            print("⚠️  v6 VALIDATION: BORDERLINE (90-95% relevance accuracy)")
        else:
            print("❌ v6 VALIDATION: NEEDS WORK (<90% relevance accuracy)")

        print("=" * 70)

    def generate_csv(self, output_path: Path = None):
        """Generate CSV report"""

        if not self.results:
            return

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = self.base_dir / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            output_path = reports_dir / f"v6_test_results_{timestamp}.csv"

        fieldnames = [
            "source_id",
            "test_category",
            "overall_pass",
            "relevance_match",
            "expected_relevance",
            "actual_relevance",
            "bariatric_context_populated",
            "bariatric_context_match",
            "expected_bariatric_context",
            "actual_bariatric_context",
            "treatments_match",
            "expected_treatments",
            "actual_treatments",
            "relevance_reason",
            "v6_rule",
            "notes"
        ]

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                row = {
                    "source_id": result["source_id"],
                    "test_category": result["test_category"],
                    "overall_pass": "PASS" if result["overall_pass"] else "FAIL",
                    "relevance_match": "PASS" if result["relevance_match"] else "FAIL",
                    "expected_relevance": result["expected_relevance"],
                    "actual_relevance": result["actual_relevance"],
                    "bariatric_context_populated": "YES" if result["bariatric_context_populated"] else "NO",
                    "bariatric_context_match": "PASS" if result["bariatric_context_match"] else "FAIL",
                    "expected_bariatric_context": result["expected_bariatric_context"],
                    "actual_bariatric_context": result["actual_bariatric_context"],
                    "treatments_match": "PASS" if result["treatments_match"] else "FAIL",
                    "expected_treatments": ", ".join(result["expected_treatments"]),
                    "actual_treatments": ", ".join(result["actual_treatments"]),
                    "relevance_reason": result["relevance_reason"],
                    "v6_rule": result["v6_rule"],
                    "notes": "; ".join(result["notes"])
                }
                writer.writerow(row)

        print(f"\n📄 CSV report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Score PBH SIGNAL v6 test results")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed per-test results")
    parser.add_argument("--csv", action="store_true",
                        help="Generate CSV report")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    scorer = V6Scorer(base_dir)

    if not scorer.load_expected_outcomes():
        return

    scorer.run_scoring(verbose=args.verbose)
    scorer.print_summary()

    if args.csv:
        scorer.generate_csv()


if __name__ == "__main__":
    main()
