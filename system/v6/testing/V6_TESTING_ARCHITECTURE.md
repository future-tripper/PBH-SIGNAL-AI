# v6 Testing Architecture

## Overview

Unlike v5's simulated test cases with hand-crafted expected outputs, v6 testing uses **real pipeline data** where we can only define expected values for key fields. The primary goal is validating the **expanded relevance logic**.

## Key Differences from v5

| Aspect | v5 Approach | v6 Approach |
|--------|------------|-------------|
| **Test Data** | 44 simulated cases | 45 real posts from CSV |
| **Expected Outputs** | Full enriched JSON for each test | Only critical fields (relevance_label, bariatric_context, treatments) |
| **Scoring Focus** | Field-by-field comparison | Relevance accuracy + key field validation |
| **Entity Extraction** | Exact match expected | Not validated (too variable for real data) |

## Architecture Components

### 1. CSV to Normalized JSON Converter (`csv_to_normalized.py`)

**Purpose:** Convert CSV rows to normalized JSON format matching the enrichment input schema.

**Input:**
- `data-everything.csv` (1,000 rows)
- List of source_ids to extract (45 test candidates)

**Output:**
- Directory of normalized JSON files (one per test post)

**Field Mapping:**
```
CSV Column          → JSON Field
-----------------------------------------
source             → source
source_id          → source_id
url                → url
title              → title
text               → text
parent_source      → parent_source
subsource          → subsource
country            → country
language           → language
published_at       → published_at
sentiment          → sentiment_raw (passthrough)
author_id          → author.id
likes              → metrics.likes
comments           → metrics.comments
shares             → metrics.shares
```

### 2. Expected Outputs Manifest (`v6_expected_outcomes.json`)

**Purpose:** Define expected values for critical fields based on v6 rules.

**Structure:**
```json
{
  "test_posts": [
    {
      "source_id": "t3_1ph44gy",
      "test_category": "bariatric_context_only",
      "expected_relevance_label": "borderline",
      "expected_bariatric_context": "strong",
      "expected_treatments": [],
      "v6_rule": "Strong bariatric context without PBH indicators → borderline"
    },
    {
      "source_id": "t3_1pgthw4",
      "test_category": "pbh_mention",
      "expected_relevance_label": "relevant",
      "expected_bariatric_context": "strong",
      "expected_treatments": [],
      "v6_rule": "Explicit reactive hypoglycemia mention → relevant"
    }
  ]
}
```

### 3. v6 Test Runner (`run_tests_v6.py`)

**Purpose:** Run enrichment on normalized JSON files using v6 configuration.

**Configuration:**
- System prompt: `openai_assistant_system_prompt_v6_with_dictionary.md`
- Response format: `openai_assistant_response_format_v6.json`
- Model: `gpt-4o-2024-11-20`
- Temperature: 0.3

**Output:**
- Directory of enriched JSON files (one per test post)
- Processing log with timing

### 4. v6 Scoring Script (`score_results_v6.py`)

**Purpose:** Compare actual outputs against expected outcomes.

**Primary Metrics:**
1. **relevance_label accuracy** (CRITICAL)
   - Exact match required
   - Track: correct, wrong category, false negatives, false positives

2. **bariatric_context populated** (CRITICAL)
   - Must be "strong", "weak", or "none" (never empty/NaN)
   - Match expected value if defined

3. **treatments extraction** (IMPORTANT)
   - Check PBH_TREATMENTS detected when expected
   - Check GLP1_TREATMENTS detected when expected

**Relaxed/Skip:**
- topics, symptoms, conditions - too variable
- sentiment, emotions, intent - subjective
- key_phrases - highly variable

**Output:**
- Console summary with pass/fail rates
- CSV report with per-test results
- Aggregate metrics for v6 validation

### 5. Directory Structure

```
system/v6/testing/
├── V6_TESTING_ARCHITECTURE.md      # This document
├── README.md                        # Quick start guide
├── extract_test_candidates.py       # Already created
├── csv_to_normalized.py             # CSV → JSON converter
├── run_tests_v6.py                  # Test runner
├── score_results_v6.py              # Scoring script
├── v6_expected_outcomes.json        # Expected values manifest
├── .env.example                     # API key template
├── requirements.txt                 # Dependencies
├── test_candidates/                 # Extracted candidates (already created)
│   ├── all_test_candidates.csv
│   └── changed_relevance_candidates.csv
├── normalized_inputs/               # Normalized JSON test inputs
│   └── [source_id].json
├── enriched_outputs/                # Enriched JSON outputs
│   └── [source_id]_enriched.json
└── reports/                         # Test results
    └── v6_test_results_[timestamp].csv
```

## Testing Workflow

### Phase 1: Preparation
1. ✅ Extract test candidates from CSV (`extract_test_candidates.py`)
2. Create expected outcomes manifest (`v6_expected_outcomes.json`)
3. Convert CSV rows to normalized JSON (`csv_to_normalized.py`)

### Phase 2: Execution
4. Set up `.env` with OpenAI API key
5. Run test suite (`run_tests_v6.py`)
6. Wait for completion (~23 minutes at 30s/test for 45 tests)

### Phase 3: Analysis
7. Run scoring script (`score_results_v6.py`)
8. Review results and identify issues
9. Iterate on v6 prompt/dictionary if needed

## Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| relevance_label accuracy | ≥95% | Primary v6 goal |
| False negatives (bariatric → not_relevant) | 0 | Critical v6 fix |
| bariatric_context populated | 100% | Must never be NaN |
| PBH treatments → relevant | 100% | Core v6 change |
| GLP-1 + bariatric → relevant | ≥90% | New v6 rule |

## Expected Outcomes by Category

Based on `changed_relevance_candidates.csv`:

| Category | Count | v5 Result | v6 Expected |
|----------|-------|-----------|-------------|
| bariatric_context only | 33 | not_relevant | borderline |
| glp1_treatment (no bariatric) | 8 | not_relevant | borderline |
| glp1_treatment + bariatric | 5 | not_relevant | relevant |
| pbh_mention | 3 | not_relevant | relevant |
| pbh_treatment | 1 | not_relevant | relevant |

## API Cost Estimate

- 45 tests × ~4,000 tokens/test = ~180,000 tokens
- At GPT-4o pricing (~$5/1M input, $15/1M output)
- Estimated cost: ~$2-3 per full test run
