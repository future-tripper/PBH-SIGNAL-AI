# v6 Testing Framework

## Overview

v6 testing uses **real pipeline data** from `data-everything.csv` (1,000 posts) to validate the expanded relevance logic. Unlike v5's simulated test cases, we identify posts that SHOULD change under v6 rules and verify the new system produces correct outputs.

## Key v6 Changes Being Tested

1. **PBH Treatments → "relevant"**: acarbose, diazoxide, octreotide, avexitide
2. **GLP-1s + bariatric context → "relevant"**: semaglutide, tirzepatide, etc.
3. **Bariatric context alone → "borderline"**: (was "not_relevant" in v5)
4. **Dictionary misspellings**: acrobose, acarobose added for acarbose

## Test Candidates Extracted

From 1,000 real posts, we identified:

| Category | Count | Expected v6 Relevance |
|----------|-------|----------------------|
| Total candidates with triggers | 64 | - |
| Posts that would change | 45 | - |
| bariatric_context | 46 | borderline |
| glp1_treatment | 13 | borderline (or relevant with bariatric) |
| pbh_mention | 5 | relevant |
| pbh_treatment | 1 | relevant |

## Directory Structure

```
testing/
├── README.md                          # This file
├── extract_test_candidates.py         # Script to identify test posts
├── test_candidates/
│   ├── all_test_candidates.csv        # All 64 posts with triggers
│   └── changed_relevance_candidates.csv # 45 posts that should change
└── v6_test_results/                   # (created after testing)
    └── comparison_report.csv
```

## Testing Workflow

### Phase 1: Setup (COMPLETE)

1. ✅ Created v6 enrichment system (prompt, dictionary, schema)
2. ✅ Updated reference schemas to v6
3. ✅ Extracted test candidates from real data

### Phase 2: Run v6 Enrichment

**For Dev Team:**

1. Deploy v6 enrichment system to pipeline:
   - Use `system/v6/enrichment/openai_assistant_system_prompt_v6_with_dictionary.md`
   - Use `system/v6/enrichment/openai_assistant_response_format_v6.json`

2. Re-process the posts from `changed_relevance_candidates.csv`:
   - 45 specific posts identified by `source_id`
   - Can also process full 1,000-post dataset for comprehensive validation

3. Export enriched results to CSV

### Phase 3: Validate Results

**Expected Outcomes:**

| Post Type | v5 Result | v6 Expected |
|-----------|-----------|-------------|
| Posts with bariatric keywords (46) | not_relevant | borderline |
| Posts with GLP-1 + bariatric (varies) | not_relevant | relevant |
| Posts with PBH treatments (1) | not_relevant | relevant |
| Posts with explicit PBH mention (5) | relevant/varies | relevant |

**Validation Criteria:**

1. **relevance_label accuracy**: Primary test - do posts match expected tier?
2. **bariatric_context populated**: Must be "strong", "weak", or "none" (never NaN)
3. **treatments extracted**: PBH treatments and GLP-1s correctly identified
4. **False negative reduction**: Previously "not_relevant" posts now appropriately tagged

### Phase 4: Report & Iterate

1. Generate comparison report
2. Identify remaining false negatives/positives
3. Adjust v6 prompt/dictionary as needed
4. Re-run until satisfied

## Quick Start

```bash
# Extract test candidates (already done)
cd system/v6/testing
python extract_test_candidates.py \
    ../phase2/data-everything.csv \
    ./test_candidates/

# Review candidates
open test_candidates/changed_relevance_candidates.csv
```

## Success Criteria

| Metric | Target |
|--------|--------|
| False negatives (bariatric posts → not_relevant) | 0 |
| PBH treatment posts → relevant | 100% |
| Bariatric context populated (not NaN) | 100% |
| Overall relevance accuracy | ≥95% |

## Files for Dev Team

Enrichment configuration to deploy:

1. **System Prompt**: `system/v6/enrichment/openai_assistant_system_prompt_v6_with_dictionary.md`
2. **Response Schema**: `system/v6/enrichment/openai_assistant_response_format_v6.json`
3. **Reference**: `reference_schemas/PBH_SIGNAL_ENRICHMENT_SCHEMA_v6.csv`

## Contact

Questions about v6 testing? Reference:
- `CLAUDE.md` for overall project context
- `reference_schemas/README.md` for v6 change summary
- Test candidates in `test_candidates/*.csv` for specific posts to validate
