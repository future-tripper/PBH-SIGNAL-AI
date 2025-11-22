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

**Ready for Dev Testing:** v5 Comprehensive Edge Case Coverage
- **Platforms:** 4-platform MVP (Reddit, TikTok, Facebook, Instagram)
- **Test Coverage:** 44 comprehensive test cases across 6 categories
- **Testing Phase:** Dev team runs automated test suite → TCD reviews real sample data
- **Success Target:** ≥98% accuracy (maintaining v3 benchmark)
- **Previous:** v4 MVP Platform Coverage (14 real production cases)

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
├── system/                                   # Versioned systems (renamed from enrichment_system)
│   ├── enrichment-system-v1/               # Baseline (80% accuracy)
│   ├── enrichment-system-v2/               # Reddit-only (91% accuracy)
│   ├── enrichment-system-v3/               # Multi-platform (98% accuracy)
│   ├── enrichment-system-v4/               # 5-platform MVP (14 real test cases)
│   └── v5/                                 # Comprehensive system (enrichment + chatbot) (CURRENT)
│       ├── enrichment/                     # Enrichment subsystem
│       │   ├── PBH_SIGNAL_DICTIONARY_v5.txt
│       │   ├── openai_assistant_system_prompt_v5.md
│       │   ├── openai_assistant_response_format_v5.json
│       │   └── normalization_schema_v5.json
│       ├── chatbot/                        # Chatbot subsystem
│       │   └── chatbot_system_prompt_v5.md (placeholder)
│       ├── enrichment-test-data-v5/        # 44 test cases (6 categories)
│       │   ├── ae-test-cases/              # Adverse event detection (12 tests)
│       │   ├── platform-coverage/          # Platform diversity (8 tests)
│       │   ├── edge-cases/                 # Schema edge cases (8 tests)
│       │   ├── dictionary-tests/           # Entity extraction robustness (6 tests)
│       │   ├── classification-tests/       # Audience/sentiment nuance (6 tests)
│       │   ├── flag-tests/                 # Crisis/misattribution flags (4 tests)
│       │   └── expected-outputs/           # Golden standard outputs (organized by category)
│       └── v5-test-package/                # Testing infrastructure
│           ├── phase1_test_results.csv     # Detailed test tracking CSV
│           ├── phase1_claude_prompt.md     # Claude Code comparison instructions
│           ├── phase2_review_template.csv  # Real sample review tracking
│           ├── TESTING_GUIDE.md            # Complete 3-phase testing workflow
│           ├── README.md                   # Quick reference
│           └── automation/                 # Python automation scripts (Responses API)
└── [Root Level - Active Files]              # Current working versions
    ├── PBH_SIGNAL_DICTIONARY.txt           # Entity extraction rules
    ├── openai_assistant_system_prompt.md   # AI instructions
    └── openai_assistant_response_format.json # Output schema
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

### Current Testing Status (2025-11-21):
**Approach:** Automated Responses API testing (system/v5/v5-test-package/automation/)
- ✅ Vector store created: vs_6920c1b62b2081919d3b8d32637d6c80
- ✅ Dictionary uploaded: PBH_SIGNAL_DICTIONARY_v5.txt
- ⚠️ Fixing: Responses API tool_resources parameter issue
- 📋 TODO: Run 44 tests, compare outputs, populate phase1_test_results.csv

**Key Change (2025-11-21):** Event-based AE detection - no dictionary symptoms required

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