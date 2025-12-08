# PBH SIGNAL v5 Testing Infrastructure

Organized testing framework for validating the v5 enrichment system across simulated and real-world data.

## Folder Structure

```
testing/
├── README.md                    # This file
├── TESTING_GUIDE.md            # Complete 3-phase testing workflow
├── phase1/                      # Simulated data testing (44 test cases)
│   ├── phase1_claude_prompt.md  # Instructions for Claude Code comparison
│   ├── phase1_test_results_template.csv  # Results tracking template
│   ├── compare_results.py       # Automated comparison script
│   └── run_tests_chat.py        # Test runner using Chat API
├── phase2/                      # Real-world data testing
│   ├── phase2_review_template.csv        # Manual review tracking (legacy)
│   ├── phase2_test_results.csv           # Automated results tracking
│   ├── SIGNAL_v5_real_enriched_data_CLEAN.csv  # Cleaned real-world data (v5 only)
│   └── phase2_evaluation_prompt.md       # Claude Code evaluation instructions
└── shared/                      # Shared utilities
    └── generate_report.py       # Report generator (works with both phases)
```

## Testing Phases

### Phase 1: Simulated Data Testing
- **Purpose:** Validate enrichment against 44 pre-defined test cases with known expected outputs
- **Method:** Compare actual outputs vs golden standard expected outputs
- **Success Criteria:**
  - Tier 1 (Critical/Safety): ≥90% pass rate
  - Tier 2 (Core Product): ≥80% pass rate
- **Files:**
  - Test inputs: `../enrichment-test-data-v5/{category}/`
  - Expected outputs: `../enrichment-test-data-v5/expected-outputs/{category}/`

### Phase 2: Real-World Data Testing
- **Purpose:** Validate enrichment quality on actual production data
- **Method:** Claude Code evaluates raw post content against enrichment output
- **Success Criteria:**
  - No critical issues (missed AE flags, wrong relevance on clear cases)
  - High confidence in production readiness
- **Data Source:** Dev team provides enriched CSV from production pipeline

### Phase 3: Dashboard/Chatbot Testing
- **Purpose:** End-to-end validation of UI and chatbot functionality
- **Method:** Manual testing of dashboard features and chatbot responses
- **Documentation:** See TESTING_GUIDE.md

## How to Run

### Phase 1 (Simulated)
```bash
# 1. Run tests through enrichment pipeline (dev team)
# 2. Save outputs to actual_outputs/
# 3. Run comparison
cd phase1/
python compare_results.py

# 4. Generate report
cd ../shared/
python generate_report.py
```

### Phase 2 (Real-World)
```bash
# 1. Receive enriched CSV from dev team
# 2. Clean data (keep only v5-compliant rows)
# 3. Use Claude Code to evaluate each post
# 4. Populate phase2_test_results.csv
# 5. Generate report using shared/generate_report.py
```

## Tier Definitions

| Tier | Fields | Threshold | Rationale |
|------|--------|-----------|-----------|
| **Tier 1** (Critical/Safety) | flags, relevance_label, audience_label, bariatric_context | ≥90% | Patient safety, FDA compliance |
| **Tier 2** (Core Product) | sentiment_label, engagement_label | ≥80% | Product quality |
| **Tier 3** (Enhancements) | themes, emotions, intent | Track only | Subjective fields |

## Version History

- **v5.3.4** (2025-11-24): TCD internal testing complete, 93.2% Tier 1 pass rate
- **v5.3.4** (2025-12-04): Phase 2 real-world data review in progress
