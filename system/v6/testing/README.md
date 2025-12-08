# v6 Testing Framework

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 3. Run tests (45 tests, ~23 minutes at 30s/test)
python run_tests_v6.py

# 4. Score results
python score_results_v6.py --csv
```

## Overview

v6 testing validates the **expanded relevance logic** using 45 real posts from the production pipeline that were incorrectly marked as `not_relevant` in v5.

### What v6 Fixes

| Issue | v5 Behavior | v6 Expected |
|-------|-------------|-------------|
| Bariatric posts without PBH | → not_relevant | → borderline |
| PBH treatments (acarbose, etc.) | → borderline (weak context) | → relevant |
| GLP-1s + bariatric context | → not_relevant | → relevant |

### Test Categories

| Category | Count | Expected Relevance |
|----------|-------|-------------------|
| bariatric_context_only | 23 | borderline |
| weak_bariatric | 12 | borderline |
| glp1_only | 7 | borderline |
| pbh_mention | 3 | relevant |

## Directory Structure

```
testing/
├── README.md                          # This file
├── V6_TESTING_ARCHITECTURE.md         # Detailed architecture docs
├── requirements.txt                   # Python dependencies
├── .env.example                       # API key template
│
├── # Data Preparation
├── extract_test_candidates.py         # Identify test posts from CSV
├── csv_to_normalized.py               # Convert CSV → normalized JSON
├── generate_expected_outcomes.py      # Create expected outcomes manifest
│
├── # Test Execution
├── run_tests_v6.py                    # Run enrichment via Chat Completions
│
├── # Analysis
├── score_results_v6.py                # Score results against expectations
│
├── # Data Files
├── test_candidates/
│   ├── all_test_candidates.csv        # 64 posts with relevant triggers
│   └── changed_relevance_candidates.csv # 45 posts that should change
├── normalized_inputs/                 # 45 normalized JSON test inputs
├── enriched_outputs/                  # Enriched JSON outputs (after running)
├── v6_expected_outcomes.json          # Expected values for scoring
└── reports/                           # CSV test reports
```

## Detailed Usage

### Step 1: Verify Setup (Already Done)

Test candidates and normalized inputs were already created:

```bash
# These were run during setup:
python extract_test_candidates.py    # Found 45 test candidates
python csv_to_normalized.py          # Created 45 normalized JSON files
python generate_expected_outcomes.py # Created expected outcomes manifest
```

### Step 2: Run Tests

```bash
# Run all 45 tests (default 30s delay between calls)
python run_tests_v6.py

# Run faster (10s delay) - may hit rate limits
python run_tests_v6.py --delay 10

# Run single test
python run_tests_v6.py --source-id t3_1ph44gy

# Run first 5 tests only
python run_tests_v6.py --limit 5
```

**Expected runtime:** ~23 minutes for 45 tests at 30s/test

### Step 3: Score Results

```bash
# Basic scoring with summary
python score_results_v6.py

# Verbose output (per-test details)
python score_results_v6.py --verbose

# Generate CSV report
python score_results_v6.py --csv
```

## Success Criteria

| Metric | Target | Description |
|--------|--------|-------------|
| Relevance accuracy | ≥95% | Primary v6 validation metric |
| bariatric_context populated | 100% | Must never be empty/NaN |
| False negatives | 0 | No bariatric posts → not_relevant |

## Output Example

```
📊 PRIMARY METRIC: Relevance Label Accuracy
   ✅ Correct: 43/45 (95.6%)
   ❌ Wrong: 2/45 (4.4%)

📊 BY CATEGORY:
   bariatric_context_only (23 tests):
      Relevance: 22/23 (96%)
   weak_bariatric (12 tests):
      Relevance: 12/12 (100%)
   glp1_only (7 tests):
      Relevance: 6/7 (86%)
   pbh_mention (3 tests):
      Relevance: 3/3 (100%)

🎉 v6 VALIDATION: PASSED (≥95% relevance accuracy)
```

## Troubleshooting

### API Key Issues
```
❌ Error: OPENAI_API_KEY not found
```
→ Copy `.env.example` to `.env` and add your API key

### Rate Limiting
```
❌ API Error: RateLimitError
```
→ Increase delay: `python run_tests_v6.py --delay 60`

### Missing Files
```
❌ Error: normalized_inputs directory not found
```
→ Run: `python csv_to_normalized.py`

## Files for Dev Team

When deploying v6 to production, use:

1. **System Prompt:** `../enrichment/openai_assistant_system_prompt_v6_with_dictionary.md`
2. **Response Schema:** `../enrichment/openai_assistant_response_format_v6.json`
3. **Reference:** `reference_schemas/PBH_SIGNAL_ENRICHMENT_SCHEMA_v6.csv`
