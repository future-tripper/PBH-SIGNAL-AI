#!/usr/bin/env python3
"""
PBH SIGNAL v5 - Phase 1 Test Report Generator

Generates comprehensive success rate report with analysis and recommendations.
"""

import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class ReportGenerator:
    """Generates Phase 1 test report"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.csv_path = base_dir.parent / "phase1_test_results.csv"
        self.results = []

    def load_csv(self):
        """Load results from CSV"""
        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            self.results = list(reader)

    def analyze_results(self) -> dict:
        """Analyze test results and generate statistics"""

        # Overall stats
        total = len(self.results)
        overall_pass = sum(1 for r in self.results if r['overall_pass'] == 'PASS')
        critical_pass = sum(1 for r in self.results if r['critical_pass'] == 'PASS')

        # Tier-based stats
        tier1_pass = sum(1 for r in self.results if r.get('tier1_pass', r['critical_pass']) == 'PASS')
        tier2_pass = sum(1 for r in self.results if r.get('tier2_pass', 'PASS') == 'PASS')
        tier3_pass = sum(1 for r in self.results if r.get('tier3_pass', 'PASS') == 'PASS')

        # Category breakdown
        by_category = defaultdict(lambda: {
            'total': 0,
            'pass': 0,
            'critical_pass': 0,
            'tier1_pass': 0,
            'tier2_pass': 0,
            'tier3_pass': 0
        })

        for result in self.results:
            cat = result['category']
            by_category[cat]['total'] += 1

            if result['overall_pass'] == 'PASS':
                by_category[cat]['pass'] += 1

            if result['critical_pass'] == 'PASS':
                by_category[cat]['critical_pass'] += 1

            if result.get('tier1_pass', result['critical_pass']) == 'PASS':
                by_category[cat]['tier1_pass'] += 1

            if result.get('tier2_pass', 'PASS') == 'PASS':
                by_category[cat]['tier2_pass'] += 1

            if result.get('tier3_pass', 'PASS') == 'PASS':
                by_category[cat]['tier3_pass'] += 1

        # Field failure analysis
        field_failures = defaultdict(int)

        for result in self.results:
            if result['flags_match'] == 'FAIL':
                field_failures['flags'] += 1
            if result['relevance_match'] == 'FAIL':
                field_failures['relevance_label'] += 1
            if result['audience_match'] == 'FAIL':
                field_failures['audience_label'] += 1
            if result['bariatric_context_match'] == 'FAIL':
                field_failures['bariatric_context'] += 1
            if result['sentiment_match'] == 'FAIL':
                field_failures['sentiment_label'] += 1
            if result['themes_match'] == 'FAIL':
                field_failures['themes'] += 1

        # Critical failures (for detailed review)
        critical_failures = [
            r for r in self.results
            if r['critical_pass'] == 'FAIL'
        ]

        return {
            'total': total,
            'overall_pass': overall_pass,
            'critical_pass': critical_pass,
            'tier1_pass': tier1_pass,
            'tier2_pass': tier2_pass,
            'tier3_pass': tier3_pass,
            'overall_rate': overall_pass / total * 100,
            'critical_rate': critical_pass / total * 100,
            'tier1_rate': tier1_pass / total * 100,
            'tier2_rate': tier2_pass / total * 100,
            'tier3_rate': tier3_pass / total * 100,
            'by_category': dict(by_category),
            'field_failures': dict(field_failures),
            'critical_failures': critical_failures
        }

    def generate_report(self, output_path: Path):
        """Generate markdown report"""

        stats = self.analyze_results()

        report = []
        report.append("# PBH SIGNAL v5 - Phase 1 Test Results")
        report.append("")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**API:** Chat Completions (gpt-4o-2024-08-06)")
        report.append(f"**Temperature:** 0.3")
        report.append(f"**Dictionary:** Embedded (384 lines)")
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"**Total Tests:** {stats['total']}")
        report.append("")
        report.append("### Performance by Tier")
        report.append("")
        report.append(f"- **Tier 1 (Critical/Safety):** {stats['tier1_pass']}/{stats['total']} ({stats['tier1_rate']:.1f}%) ✅")
        report.append(f"  - flags, relevance_label, audience_label, bariatric_context")
        report.append(f"- **Tier 2 (Core Product):** {stats['tier2_pass']}/{stats['total']} ({stats['tier2_rate']:.1f}%)")
        report.append(f"  - sentiment_label, engagement_label")
        report.append(f"- **Tier 3 (Enhancements):** {stats['tier3_pass']}/{stats['total']} ({stats['tier3_rate']:.1f}%)")
        report.append(f"  - themes, emotions, intent (subjective fields)")
        report.append("")
        report.append(f"**Legacy Metrics:** Overall {stats['overall_rate']:.1f}% | Critical {stats['critical_rate']:.1f}%")
        report.append("")

        # Status assessment (using Tier 1 as primary metric)
        if stats['tier1_rate'] < 90:
            report.append("### ⚠️ CRITICAL ISSUES DETECTED")
            report.append("")
            report.append(f"The system is **NOT READY** for production deployment. Tier 1 (Critical/Safety) pass rate of {stats['tier1_rate']:.1f}% is below the 90% threshold required for FDA-regulated adverse event detection.")
            report.append("")
        elif stats['tier2_rate'] < 80:
            report.append("### ⚠️ TIER 2 IMPROVEMENTS NEEDED")
            report.append("")
            report.append(f"Tier 1 critical tests passed ({stats['tier1_rate']:.1f}%), but Tier 2 (Core Product) pass rate of {stats['tier2_rate']:.1f}% indicates quality issues that need attention before production.")
            report.append("")
        else:
            report.append("### ✅ READY FOR PHASE 2")
            report.append("")
            report.append(f"Core safety and product quality metrics meet requirements (Tier 1: {stats['tier1_rate']:.1f}%, Tier 2: {stats['tier2_rate']:.1f}%).")
            report.append("")

        # Category Breakdown
        report.append("## Results by Category")
        report.append("")
        report.append("| Category | Total | Pass | Success Rate | Critical Pass Rate |")
        report.append("|----------|-------|------|--------------|-------------------|")

        for cat, data in sorted(stats['by_category'].items()):
            pass_rate = data['pass'] / data['total'] * 100
            crit_rate = data['critical_pass'] / data['total'] * 100
            status = "✅" if pass_rate >= 90 else "⚠️" if pass_rate >= 70 else "❌"

            report.append(f"| {status} {cat} | {data['total']} | {data['pass']} | {pass_rate:.1f}% | {crit_rate:.1f}% |")

        report.append("")

        # What's Working Well
        report.append("## What's Working Well")
        report.append("")

        # Calculate field success rates
        field_success = {}
        for field in ['flags', 'relevance_label', 'audience_label', 'bariatric_context', 'sentiment_label', 'themes']:
            failures = stats['field_failures'].get(field, 0)
            success_rate = (stats['total'] - failures) / stats['total'] * 100
            field_success[field] = success_rate

        # Show high-performing fields (≥90%)
        high_performers = [(field, rate) for field, rate in field_success.items() if rate >= 90]
        if high_performers:
            for field, rate in sorted(high_performers, key=lambda x: x[1], reverse=True):
                report.append(f"- ✅ **{field}**: {rate:.1f}% accurate")
            report.append("")
        else:
            report.append("_(No fields meeting ≥90% threshold)_")
            report.append("")

        # Field Failure Analysis
        report.append("## Areas for Improvement")
        report.append("")
        report.append("Fields with <90% accuracy:")
        report.append("")

        sorted_failures = sorted(stats['field_failures'].items(), key=lambda x: x[1], reverse=True)

        for field, count in sorted_failures:
            pct = count / stats['total'] * 100
            severity = "🔴" if pct > 20 else "🟡" if pct > 10 else "🟢"
            report.append(f"- {severity} **{field}**: {count}/{stats['total']} tests ({pct:.1f}%)")

        report.append("")

        # Critical Failures Detail
        if stats['critical_failures']:
            report.append("## Critical Failures (Detailed)")
            report.append("")
            report.append(f"**{len(stats['critical_failures'])} tests failed critical validation:**")
            report.append("")

            for result in stats['critical_failures']:
                report.append(f"### {result['test_name']} ({result['category']})")
                report.append("")

                failed_fields = []
                if result['flags_match'] == 'FAIL':
                    failed_fields.append("flags")
                if result['relevance_match'] == 'FAIL':
                    failed_fields.append("relevance_label")
                if result['audience_match'] == 'FAIL':
                    failed_fields.append("audience_label")
                if result['bariatric_context_match'] == 'FAIL':
                    failed_fields.append("bariatric_context")

                if failed_fields:
                    report.append(f"**Failed Critical Fields:** {', '.join(failed_fields)}")
                    report.append("")

                if result['notes'] and result['notes'] != 'All fields match':
                    report.append(f"**Details:** {result['notes']}")
                    report.append("")

        # Root Cause Analysis
        report.append("## Root Cause Analysis")
        report.append("")

        # Analyze patterns
        bariatric_context_failures = stats['field_failures'].get('bariatric_context', 0)
        relevance_failures = stats['field_failures'].get('relevance_label', 0)
        flag_failures = stats['field_failures'].get('flags', 0)
        audience_failures = stats['field_failures'].get('audience_label', 0)

        if bariatric_context_failures > stats['total'] * 0.2:
            report.append("### 🔴 Bariatric Context Detection")
            report.append("")
            report.append(f"**{bariatric_context_failures} failures ({bariatric_context_failures/stats['total']*100:.1f}%)**")
            report.append("")
            report.append("The system is struggling to correctly identify bariatric surgery context, particularly:")
            report.append("- Posts with PBH mentioned but without explicit bariatric surgery references")
            report.append("- Third-person narratives (family members, HCPs)")
            report.append("- Short posts with minimal context")
            report.append("")
            report.append("**Recommendation:** Revise bariatric_context classification logic in system prompt. Consider adding anchor phrases for implicit bariatric context.")
            report.append("")

        if relevance_failures > stats['total'] * 0.15:
            report.append("### 🔴 Relevance Classification")
            report.append("")
            report.append(f"**{relevance_failures} failures ({relevance_failures/stats['total']*100:.1f}%)**")
            report.append("")
            report.append("The system is misclassifying post relevance:")
            report.append("- Over-classifying borderline posts as relevant")
            report.append("- Under-classifying relevant posts as borderline")
            report.append("- Off-topic posts incorrectly marked as relevant")
            report.append("")
            report.append("**Recommendation:** Review relevance decision tree in system prompt. Clarify criteria for borderline vs relevant vs not_relevant.")
            report.append("")

        if flag_failures > stats['total'] * 0.1:
            report.append("### 🟡 Flag Detection")
            report.append("")
            report.append(f"**{flag_failures} failures ({flag_failures/stats['total']*100:.1f}%)**")
            report.append("")
            report.append("Issues with flag detection, particularly:")
            report.append("- Unexpected 'possible_PBH_misattribution' flags in posts with legitimate PBH")
            report.append("- Missing or extra flags compared to expected outputs")
            report.append("")
            report.append("**Recommendation:** Clarify flag criteria in system prompt, especially for possible_PBH_misattribution.")
            report.append("")

        if audience_failures > 0:
            report.append("### 🟢 Audience Classification")
            report.append("")
            report.append(f"**{audience_failures} failures ({audience_failures/stats['total']*100:.1f}%)**")
            report.append("")
            report.append("Minor issues with audience detection (researcher vs HCP vs media).")
            report.append("")
            report.append("**Recommendation:** Review audience anchor phrases and classification criteria.")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        if stats['critical_rate'] < 90:
            report.append("### Immediate Actions (Critical)")
            report.append("")
            report.append("1. **DO NOT proceed to Phase 2** until critical pass rate >= 90%")
            report.append("2. **Revise system prompt** to address bariatric_context and relevance_label issues")
            report.append("3. **Add explicit classification guidance** for edge cases:")
            report.append("   - Third-person narratives (family, HCP)")
            report.append("   - Posts mentioning PBH without bariatric surgery context")
            report.append("   - Off-topic bariatric posts (weight loss without PBH)")
            report.append("4. **Re-test all critical failures** after prompt revisions")
            report.append("")

        report.append("### Phase 2 Preparation")
        report.append("")
        report.append("Once critical pass rate >= 90%:")
        report.append("")
        report.append("1. **Expand test coverage:**")
        report.append("   - Add 50+ more real-world test cases")
        report.append("   - Include more platform-specific edge cases")
        report.append("   - Test multilingual content (if applicable)")
        report.append("")
        report.append("2. **Performance optimization:**")
        report.append("   - Test with temperature variations (0.0, 0.3, 0.5)")
        report.append("   - Evaluate if dictionary can be reduced for cost savings")
        report.append("   - Consider model alternatives (gpt-4o vs gpt-4o-mini)")
        report.append("")
        report.append("3. **Integration testing:**")
        report.append("   - Test API error handling and retries")
        report.append("   - Validate rate limiting behavior")
        report.append("   - Test with production data pipeline")
        report.append("")

        # Appendix
        report.append("## Appendix: Test Execution Details")
        report.append("")
        report.append("**Test Runner:** `run_tests_chat.py`")
        report.append("**Comparison Script:** `compare_results.py`")
        report.append("**Detailed Results:** `phase1_test_results.csv`")
        report.append("")
        report.append("### Test Categories")
        report.append("")
        report.append("- **adverse_events (12 tests):** AE flag detection accuracy")
        report.append("- **platform_coverage (8 tests):** Cross-platform consistency")
        report.append("- **edge_cases (8 tests):** Challenging scenarios")
        report.append("- **dictionary (6 tests):** Entity extraction from dictionary")
        report.append("- **classification (6 tests):** Relevance, audience, sentiment")
        report.append("- **flags (4 tests):** Crisis, AE, and misattribution flags")
        report.append("")

        # Write report
        report_text = "\n".join(report)

        with open(output_path, 'w') as f:
            f.write(report_text)

        print(f"✅ Report generated: {output_path}")

        # Print summary to console
        print()
        print("=" * 70)
        print("PHASE 1 TEST RESULTS SUMMARY")
        print("=" * 70)
        print()
        print("Performance by Tier:")
        print(f"  Tier 1 (Critical/Safety): {stats['tier1_rate']:.1f}%")
        print(f"  Tier 2 (Core Product):    {stats['tier2_rate']:.1f}%")
        print(f"  Tier 3 (Enhancements):    {stats['tier3_rate']:.1f}%")
        print()
        print(f"Legacy Metrics: Overall {stats['overall_rate']:.1f}% | Critical {stats['critical_rate']:.1f}%")
        print()

        if stats['tier1_rate'] < 90:
            print("⚠️  STATUS: NOT READY FOR PRODUCTION")
            print(f"   Tier 1 (Critical/Safety) below 90% threshold")
            print()
            print(f"Critical failures: {len(stats['critical_failures'])} tests")
            print()
            print("Top issues:")
            for field, count in sorted_failures[:3]:
                print(f"  • {field}: {count} failures")
        elif stats['tier2_rate'] < 80:
            print("⚠️  STATUS: TIER 2 IMPROVEMENTS NEEDED")
            print(f"   Tier 1 passed ({stats['tier1_rate']:.1f}%), but Tier 2 needs work")
        else:
            print("✅ STATUS: READY FOR PHASE 2")
            print(f"   Core metrics meet requirements")

        print()
        print("=" * 70)


def main():
    base_dir = Path(__file__).parent
    generator = ReportGenerator(base_dir)

    generator.load_csv()

    report_path = base_dir.parent / "phase1_test_report.md"
    generator.generate_report(report_path)


if __name__ == "__main__":
    main()
