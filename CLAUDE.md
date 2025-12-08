# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SIGNAL is a social listening platform being developed for Amylyx Pharmaceuticals to support the launch of Avexitide, a treatment for Post-Bariatric Hypoglycemia (PBH). The platform provides pharma marketers with insights from patient voices, HCP perspectives, and treatment discussions across social media and healthcare forums.

### Platform Architecture

The data pipeline consists of four key stages:
1. **FETCHING** - Collecting data from online sources (social media, forums, etc.)
2. **NORMALIZING** - Standardizing data to common schema format
3. **ENRICHING** - AI-powered entity extraction and classification (current focus)
4. **STORING** - Database storage with filtering capabilities for dashboard and chatbot

### Current Status

**Active Development:** v6 Expanded Relevance Logic (2025-12-08)
- **Key Change:** Broader relevance to capture bariatric content (v5 marked 99%+ as not_relevant)
- **Platforms:** 4-platform MVP (Reddit, TikTok, Facebook, Instagram)
- **Testing Phase:** Analyzing real pipeline data to validate expanded relevance
- **Previous:** v5 comprehensive edge case coverage (44 test cases, 93-97% accuracy)

## Project Structure & Data Architecture

### File Structure
```
PBH-SIGNAL-AI/
├── project_docs/                             # Documentation & tracking
│   ├── ENRICHMENT_TEST_RESULTS.csv         # Test results tracker
│   └── TEST_TRACKER_GUIDE.md               # Testing documentation
├── reference_schemas/                        # Static CSV references
│   ├── PBH_SIGNAL_NORMALIZATION_SCHEMA.csv # Input format spec
│   ├── PBH_SIGNAL_ENRICHMENT_SCHEMA.csv    # Output field definitions
│   └── PBH_SIGNAL_DASHBOARD_FEATURES.csv   # Dashboard requirements
├── system/                                   # Versioned systems
│   ├── enrichment-system-v1/               # Baseline (80% accuracy)
│   ├── enrichment-system-v2/               # Reddit-only (91% accuracy)
│   ├── enrichment-system-v3/               # Multi-platform (98% accuracy)
│   ├── enrichment-system-v4/               # 5-platform MVP (14 real test cases)
│   ├── v5/                                 # Comprehensive edge case coverage (44 test cases)
│   │   ├── enrichment/                     # v5 enrichment subsystem
│   │   ├── chatbot/                        # Chatbot subsystem (placeholder)
│   │   ├── enrichment-test-data-v5/        # 44 test cases (6 categories)
│   │   └── testing/                        # Testing infrastructure
│   └── v6/                                 # CURRENT - Expanded relevance logic
│       ├── enrichment/                     # v6 enrichment subsystem
│       │   ├── PBH_SIGNAL_DICTIONARY_v6.txt
│       │   ├── openai_assistant_system_prompt_v6.md
│       │   ├── openai_assistant_system_prompt_v6_with_dictionary.md
│       │   ├── openai_assistant_response_format_v6.json
│       │   └── normalization_schema_v6.json
│       ├── chatbot/                        # Chatbot subsystem (placeholder)
│       └── testing/                        # Testing (TBD)
└── [Root Level - Active Files]              # Current working versions (deprecated - use versioned folders)
```

### Active Development Files

**Core Enrichment System (Root Level - Editable):**
1. **Dictionary** (`PBH_SIGNAL_DICTIONARY.txt`): Taxonomy-structured entity extraction rules:
   - **Category**: Target output field (audience_anchor, companies, conditions, symptoms, treatments, topics)
   - **Label**: Exact term to extract (e.g., "PBH", "Amylyx", "shakiness", "avexitide")  
   - **Variations**: Pattern examples for semantic recognition (not exhaustive)
   - **Exclude**: Negative context terms that suppress extraction
   - **Note**: Additional context or description

2. **System Prompt** (`openai_assistant_system_prompt.md`): Optimized instructions for OpenAI Assistant
3. **Response Schema** (`openai_assistant_response_format.json`): Structured JSON output format

### Version Control Strategy
- **Root files**: Current working versions (edit these during testing)
- **enrichment_system/vX/**: Stable snapshots when major improvements achieved
- **reference_schemas/**: Static CSV references (don't edit)
- **test_data/**: Test cases for validation

## Key Business Rules

### Relevance Scoring
- **Strong bariatric context**: Direct bariatric surgery mentions or known bariatric forums
- **Weak context**: Indirect phrases like "since my surgery", "post-op"
- **Relevant**: PBH mentioned OR (strong context + hypoglycemia/symptoms)
- **Borderline**: Weak context + hypoglycemia/symptoms

### Theme Mapping
Themes are derived from presence of specific dictionary tags:
- Symptoms → from symptoms field
- Treatments → from treatments field  
- Bariatric Surgery → from topics:bariatric_surgery
- Access & Coverage → from topics:access_coverage
- Diagnostics → from topics:diagnostics_monitoring
- Diet → from topics:dietary_modification

### Engagement Scoring
`engagement_score = likes + (2 * comments) + (3 * shares)`
- High: ≥20
- Medium: 10-19
- Low: <10

## Testing Protocol (v5)

### Current Testing Status (2025-12-04):

**Phase 1 (Simulated Data): ✅ COMPLETE**
- System version: v5.3.4
- Results: Tier 1 (Critical/Safety) 93.2%, Tier 2 (Core Product) 97.7%
- Test coverage: 44 test cases across 6 categories
- Archived: `system/v5/completed-test-runs/2025-11-24-v5.3.4/`

**Phase 2 (Real-World Data): ⏸️ BLOCKED - Waiting on Dev Team**
- Data received: 172 rows from dev team (2025-12-04)
- Cleaned: 51 v5-compliant rows (removed 116 unenriched + 5 invalid schema)
- **Issue:** All 51 rows are `not_relevant` + missing key fields (`bariatric_context`)
- **Report sent:** `system/v5/testing/phase2/v5_Data_Issues_Report_FINAL.docx`
- **Next steps:**
  1. Review and improve chatbot prompt (guardrails, citations, consistency)
  2. When dev team sends fixed data, re-run Phase 2 to validate real-world enrichment

**Phase 2 Approach:**
Unlike Phase 1 (comparing against pre-defined expected outputs), Phase 2 requires:
1. Reading raw post content (title + text)
2. Evaluating if enrichment is correct based on content analysis
3. Tracking pass/fail for each critical field
4. Identifying patterns and issues for system refinement

**Key Files:**
- Evaluation guide: `system/v5/testing/phase2/phase2_evaluation_prompt.md`
- Results tracking: `system/v5/testing/phase2/phase2_test_results.csv`
- Report generator: `system/v5/testing/shared/generate_report.py`

### Three-Phase Testing Workflow

**Phase 1: AI-Assisted Test Validation (Dev Team + Claude Code)**
1. **Run Tests:** Dev team feeds 44 test inputs through their enrichment pipeline
   - Uses v5 configuration (prompt, dictionary, schema from `enrichment/` folder)
   - Saves enriched outputs to `v5-test-package/actual_outputs/`
   - One JSON file per test case

2. **Compare with Claude Code:** Use AI assistant for field-by-field comparison
   - Follow instructions in `phase1_claude_prompt.md`
   - Compare actual outputs vs expected outputs (golden standards in `expected-outputs/`)
   - Populate `phase1_test_results.csv` with detailed tracking:
     - Pass/Fail per test and per component (dictionary, relevance, sentiment, audience, AE flagging, crisis)
     - Key issues found in plain English
     - Recommended fixes with specific file/section references
     - Next actions for iteration

3. **Diagnose and Iterate:** Claude Code identifies patterns and recommends fixes
   - Reference CLAUDE.md for v5 system context
   - Update dictionary, prompt, or schema as recommended
   - Re-run tests until ≥95% pass rate achieved

4. **Report to TCD:** Email/Teams completed `phase1_test_results.csv`
   - Overall pass rate (target: ≥95%, 42+/44 tests)
   - Field accuracy (target: ≥98%)
   - Critical test status (all AE and crisis tests must pass)
   - Iterations completed and fixes applied

**Phase 2: Real Sample Data Review (TCD Team)**
1. **Sample Collection:** Dev team provides real platform data samples
   - CSV format (enriched posts, easy to review in spreadsheet)
   - Diverse content types (patient posts, HCP content, off-topic, etc.)
   - Share via email/Teams

2. **TCD Review:** Validate enrichment quality on real-world data
   - Review CSV for accuracy: relevance, sentiment, entities, flags
   - Track issues using phase2_review_template.csv
   - Share findings with dev team for diagnosis

3. **Iteration:** Refine v5 system based on real data findings
   - Update dictionary, prompt, or schema as needed
   - Re-test with automated suite
   - Repeat until production-ready

**Phase 3: Front-End/Dashboard Validation (TCD + Dev Teams)**
1. **Dashboard Testing:** Verify all dashboard modules with real enriched data
   - Data visualizations, filters, High Impact Posts
   - Post relevance matches enrichment (spot check)

2. **Chatbot Testing:** Validate chatbot functionality
   - Query understanding and data accuracy
   - Source citations and edge case handling
   - System prompt: TBD (in development)
   - Test scenarios: TBD (will be defined)

3. **Production Sign-off:** Confirm system ready for production deployment
   - All dashboard features working correctly
   - Chatbot responding appropriately
   - No critical bugs or data issues

### Test Coverage (44 Cases)

**AE Test Cases (12):** Adverse event detection across severity levels, causal language, and negation
**Platform Coverage (8):** All 4 platforms with diverse content types (real data from v4)
**Edge Cases (8):** Null fields, missing data, unusual formats, schema boundary conditions
**Dictionary Tests (6):** Negation, hypothetical, exclusions, past tense, casual language, context-dependent terms
**Classification Tests (6):** Mixed roles, caregivers, researchers, off-topic, sarcasm, clinical neutral tone
**Flag Tests (4):** Crisis detection, borderline cases, multiple flags, false positives

### Success Criteria

**Phase 1 (Test Suite):**
- Pass Rate: ≥95% (42+/44 tests passing)
- Field Accuracy: ≥98% (matches v3 benchmark)
- Critical Tests: All AE flagging and crisis detection tests must pass (patient safety)
- Event-Based AE: No dictionary symptoms required (updated 2025-11-21)

**Phase 2 (Real Samples):**
- High confidence in production readiness after reviewing 20-50 real posts
- No critical issues (missed AE flags, wrong relevance classifications)
- Minor issues addressed or documented as acceptable

**Phase 3 (Dashboard/Chatbot):**
- All dashboard modules working correctly with enriched data
- Chatbot responding accurately to test queries
- No critical bugs blocking production deployment

## Implementation Notes

### Data Processing Pipeline
1. Normalize raw social feeds to standard schema
2. Apply dictionary matching for entity extraction
3. Run AI enrichment for audience, sentiment, relevance
4. Calculate derived metrics and theme rollups
5. Load to Algolia for dashboard and chatbot access

### Dashboard Requirements
- All visualizations must support toggling between THEMES and SOURCES dimensions
- High Impact Posts must include URLs/permalinks for source attribution
- Market SOV requires entity normalization (drug↔generic, brand↔company)
- Chatbot needs full enriched dataset, not just dashboard filters

### Critical Data Quality Checks
- Validate bariatric_context before relevance scoring
- Ensure proper entity normalization for SOV calculations
- Preserve source URLs for all records
- Handle exclusion contexts in dictionary matching (e.g., "novo restaurant" != Novo Nordisk)

## System Versions

### v1: Baseline (80% accuracy)
- Initial dictionary and prompt structure
- Basic entity extraction and classification
- 8/10 Reddit test cases passing

### v2: Reddit-Optimized (91% accuracy) 
- Triangulation logic for relevance scoring
- Personal vs professional context detection
- Explicit exclusion rules (r/keto, r/diabetes)
- 10/11 Reddit test cases passing

### v3: Multi-Platform Production (98% accuracy)
- **Platforms:** Reddit + TikTok fully supported
- **Test Results:** 19/19 cases passing (11 Reddit, 8 TikTok)
- **Key Features:**
  - Platform-agnostic relevance logic
  - Enhanced false positive prevention
  - Unified schema for all platforms
  - Sophisticated edge case handling

### v4: Full MVP Platform Coverage
- **Platforms:** 4-platform MVP (Reddit, TikTok, Facebook, Instagram)
- **Test Cases:** 14 real production examples from actual data sources
- **Schema Enhancement:**
  - Nested author object with demographics (gender, age, subscribers)
  - Geographic tracking (country codes)
  - Hierarchical content structure (parent_source, subsource)
  - Platform-specific metrics handling
- **Real Clinical Data:** Facebook examples include actual Amylyx PBH trial recruitment
- **Testing Approach:** Manual case-by-case validation against expected enrichment outputs
- **Result:** Validated platform coverage and schema enhancements

### v5: Comprehensive Edge Case Coverage (Ready for Dev Testing)
- **Test Coverage:** 44 test cases across 6 categories (28 from v4 + 16 new edge cases)
- **Categories:**
  - AE Test Cases (12): Adverse event detection with severity, causation, negation
  - Platform Coverage (8): All 4 MVP platforms with diverse content
  - Edge Cases (8): Null handling, missing data, schema boundaries
  - Dictionary Tests (6): Negation, hypothetical, exclusions, casual language, context-dependent
  - Classification Tests (6): Mixed roles, caregivers, researchers, sarcasm, off-topic
  - Flag Tests (4): Crisis detection, borderline, multiple flags, false positives
- **Key Features:**
  - Dictionary robustness (suppression rules, context-dependent extraction)
  - Classification nuance (sarcasm, clinical neutral, caregiver perspective)
  - Flag edge cases (crisis vs dark humor, multiple flag scenarios)
  - Real-world messiness (emoji, slang, casual language)
- **Testing Approach:** Automated test suite (run_tests.py + compare.py)
- **Structure:** Organized into enrichment/ and chatbot/ subsystems for scalability
- **Deliverable:** v5-test-package (lean, references parent enrichment/ folder)
- **Workflow:** Two-phase (automated suite → real sample review)
- **Evaluation:** Tier-based testing (Tier 1: Critical/Safety fields need ≥90%, Tier 2: Core product ≥80%, Tier 3: Enhancements tracked but not critical)
- **Future:** Chatbot subsystem placeholder ready for development

**Note on Tiers:** Not all fields are equally important. Patient safety fields (flags, relevance) require highest accuracy. Subjective fields (themes, emotions) are nice-to-have but don't block production.

### v6: Expanded Relevance Logic (Current - 2025-12-08)
- **Key Change:** Broader relevance criteria to capture more bariatric-related content
- **Problem Solved:** v5 marked 99%+ of posts as "not_relevant" because relevance required PBH/hypoglycemia
- **New Treatment Groups for Relevance:**
  - PBH_TREATMENTS: ["avexitide", "acarbose", "diazoxide", "octreotide"] - all trigger "relevant"
  - GLP1_TREATMENTS: ["semaglutide", "tirzepatide", "dulaglutide", "liraglutide", "exenatide"] - trigger "relevant" when combined with bariatric context
- **Updated Relevance Tiers:**
  - **relevant**: PBH conditions, PBH treatments (any), strong bariatric + symptoms/hypoglycemia, strong bariatric + GLP-1s
  - **borderline**: Strong bariatric context alone (general surgery discussions), weak context + symptoms
  - **not_relevant**: No bariatric context, no relevant treatments, off-topic medical content
- **Dictionary Update:** Added "acrobose" and "acarobose" misspellings to acarbose variations
- **Files:**
  - `system/v6/enrichment/openai_assistant_system_prompt_v6.md`
  - `system/v6/enrichment/openai_assistant_system_prompt_v6_with_dictionary.md`
  - `system/v6/enrichment/PBH_SIGNAL_DICTIONARY_v6.txt`
- **Testing:** Real-world validation using 45 posts from production pipeline
  - See `system/v6/testing/` for full testing framework

## v6 Testing Protocol (Current)

### Problem Statement
v5 marked 99%+ of posts as `not_relevant` because relevance required explicit PBH/hypoglycemia mentions. Analysis of 1,000 real pipeline posts showed:
- Only 6 posts marked "relevant" (0.6%)
- 39 posts with clear bariatric keywords marked "not_relevant" (false negatives)
- Posts mentioning PBH treatments (acarbose, diazoxide) not triggering relevance

### Solution: Expanded Relevance Logic
v6 broadens what counts as relevant:

| Trigger | v5 Result | v6 Result |
|---------|-----------|-----------|
| PBH treatments (acarbose, diazoxide, octreotide) | borderline (with weak context) | **relevant** |
| GLP-1s + bariatric context | not_relevant | **relevant** |
| Bariatric context alone (no PBH indicators) | not_relevant | **borderline** |

### Testing Approach
Unlike v5's simulated test cases, v6 uses **real posts from production data**:

1. **Extract Test Candidates** - Identified 45 posts from `data-everything.csv` that should change under v6 rules
2. **Define Expected Outcomes** - Auto-generated `v6_expected_outcomes.json` with expected `relevance_label` for each post
3. **Run Enrichment** - Process posts through OpenAI Chat Completions with v6 config
4. **Score Results** - Compare actual vs expected, focusing on relevance accuracy

### Test Categories (45 posts)

| Category | Count | Expected v6 Relevance | v6 Rule |
|----------|-------|----------------------|---------|
| bariatric_context_only | 23 | borderline | Strong bariatric context without PBH indicators |
| weak_bariatric | 12 | borderline | Weak bariatric context (post-op, since surgery) |
| glp1_only | 7 | borderline | GLP-1 treatment without bariatric context |
| pbh_mention | 3 | relevant | Explicit PBH/reactive hypoglycemia mention |

### Testing Scripts

```
system/v6/testing/
├── csv_to_normalized.py        # Convert CSV → normalized JSON inputs
├── generate_expected_outcomes.py # Create expected outcomes manifest
├── run_tests_v6.py             # Run enrichment via Chat Completions API
├── score_results_v6.py         # Score results against expectations
├── normalized_inputs/          # 45 JSON test inputs (ready)
├── v6_expected_outcomes.json   # Expected values (ready)
└── enriched_outputs/           # Results after running tests
```

### How to Run v6 Tests

```bash
cd system/v6/testing

# 1. Ensure .env has OPENAI_API_KEY (root .env is used)

# 2. Run tests (~23 min at 30s/test)
python run_tests_v6.py

# 3. Score results
python score_results_v6.py --csv
```

### Success Criteria

| Metric | Target | Description |
|--------|--------|-------------|
| relevance_label accuracy | ≥95% | Primary v6 validation metric |
| bariatric_context populated | 100% | Must never be empty/NaN |
| False negatives | 0 | No bariatric posts → not_relevant |

### Scoring Logic
The scoring script (`score_results_v6.py`) compares enriched outputs against `v6_expected_outcomes.json`:

- **Primary:** Does `relevance_label` match expected? (exact match required)
- **Secondary:** Is `bariatric_context` populated correctly? (strong/weak/none, never empty)
- **Tertiary:** Are expected treatments extracted? (when applicable)

We're NOT doing full field-by-field comparison - just validating the expanded relevance logic works correctly.

### Key Files for Context Recovery

If starting a new session, read these files to understand v6:
1. `CLAUDE.md` - This file (overall project context + v6 testing plan)
2. `reference_schemas/README.md` - v6 changes summary and relevance logic
3. `system/v6/testing/V6_TESTING_ARCHITECTURE.md` - Detailed testing architecture
4. `system/v6/testing/v6_expected_outcomes.json` - Expected values for 45 test posts