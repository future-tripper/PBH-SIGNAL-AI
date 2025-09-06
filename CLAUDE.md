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

### Current Development Focus

The immediate focus is building and testing the ENRICHMENT layer using OpenAI Assistant to:
- Apply dictionary-based entity extraction
- Classify relevance, audience, and sentiment
- Generate derived metrics and theme rollups
- Prepare enriched data for dashboard visualization and chatbot RAG

**Active Development Phase:**
- **STATUS:** v3 Multi-Platform system PRODUCTION READY (98.05% accuracy on 19 test cases)
- **CURRENT TASK:** v3 complete - Reddit + TikTok system validated for deployment  
- **TRACKING:** Results logged in `project_docs/ENRICHMENT_TEST_RESULTS.csv`
- **GOAL:** v3 achieved - reliable multi-platform enrichment with sophisticated business logic
- **CLAUDE ROLE:** v3 validated - prepare for v4 minor enhancements and expanded test coverage

**Claude Code Instructions:**
When user runs tests, you should:
1. **Analyze Results**: Compare OpenAI output against expected outcomes
2. **Identify Issues**: Pinpoint specific problems (missing extractions, wrong classifications, etc.)
3. **Recommend Fixes**: Suggest targeted improvements to dictionary/prompt/schema
4. **Execute Changes**: Make the recommended fixes to system files
5. **Track Progress**: Update CSV tracker and create new versions when major improvements made
6. **Iterate**: Repeat cycle until >90% accuracy achieved

**v1 Test Results Summary (8/10 passed - 80%):**
1. **reddit_example_1-4**: Core validation ✅ v1 passed
2. **reddit_example_5-8**: Edge cases & industry voice ✅ v1 passed 
3. **reddit_example_9**: Keto false positive ❌ v1 failed (marked relevant)
4. **reddit_example_10**: Nurse audience detection ❌ v1 failed (marked HCP)

**v2 System Improvements:**
- **Triangulation Logic**: Forum context + treatment signals + exclusion rules
- **Personal Experience Override**: "I developed" trumps professional role
- **Explicit Exclusion**: r/keto, r/diabetes → always not_relevant

**v2 Testing Results (Complete):**
1. **Failed Cases Fixed**: reddit_example_9 & 10 with v2 system ✅ BOTH FIXED
2. **Full Reddit Validation**: All 11 test cases validated ✅ 10/11 PASS (91% accuracy)
3. **Edge Case Success**: reddit_example_11 professional "my" vs personal "my" ✅ PASS
4. **Outstanding Issue**: reddit_example_3 minor symptom extraction regression (weakness missed)

🚨 **v3 Multi-Platform System Ready for Testing**

**v3 Development Status (September 2024):**
- **v3 Schema Finalized**: Clean, MVP-focused normalization schema (based on original root schema)
- **Location**: `enrichment_system/v3/normalization_schema_v3.json`
- **Key Decision**: Simplified approach - abandoned complex multi-field schema for proven root schema
- **Platform Support**: Reddit + TikTok using unified field structure

**v3 Schema Design Principles:**
1. **Simplicity over complexity**: Uses proven root normalization schema instead of over-engineered approach
2. **Perfect alignment**: Schema matches v2 enrichment system expectations exactly
3. **Platform-aware subsource**: `r/subreddit` for Reddit, `null` for TikTok (hashtags ≠ conversation spaces)
4. **Native formatting**: `u/username` (Reddit), `@username` (TikTok) in author_handle
5. **Clean field mapping**: `source_id`, `subsource`, `author_handle` align with v2 business logic

**v3 PREREQUISITES COMPLETED:**
1. ✅ **Schema Alignment**: Root schema adopted - perfect compatibility with v2 enrichment system
2. ✅ **Test Case Migration**: All 13 examples (11 Reddit + 2 TikTok) updated to v3 schema format
3. ✅ **Field Normalization**: Corrected subsource (r/subreddit vs null) and author_handle formats 
4. ✅ **Schema Compliance**: All test files verified against normalization_schema_v3.json
5. ✅ **Business Logic Alignment**: v2 enrichment logic will work seamlessly with v3 normalized data

🚨 **CRITICAL: v3 System Prompt Requires Multi-Platform Updates**

**DISCOVERED ISSUE**: v3 system prompt is Reddit-only and will fail on TikTok data

**Specific Problems Found:**
- **Line 265**: "Scope: Reddit inputs (we'll add FB/IG/TikTok later)" - explicitly excludes TikTok
- **Lines 272-287**: All few-shot examples use old Reddit format (`platform`, `subreddit`, `post_id`, `author_id`)
- **Lines 75,79,82,95,101**: Hardcoded Reddit subsource logic won't handle TikTok `subsource: null`
- **bariatric_context logic**: Only recognizes Reddit subreddits, TikTok will always be "none"
- **relevance_label**: Will likely mark TikTok as "not_relevant" due to missing bariatric_context

**Required Fixes (BEFORE TESTING):**
1. **Update scope statement**: Remove Reddit-only limitation
2. **Add TikTok examples**: Create few-shot examples with TikTok v3 format
3. **Expand bariatric_context**: Add TikTok-specific strong context indicators (hashtags, profile context)
4. **Platform-agnostic logic**: Handle `subsource: null` appropriately for TikTok
5. **Fix example format**: Update Reddit examples to use v3 schema format

**v2/v3 Strategy:**
- **v2 PRESERVED**: Reddit-only system remains production-ready (91% accuracy) - DO NOT MODIFY
- **v3 BLOCKED**: System prompt updates required before testing - TikTok data will fail with current prompt
- **ROLLBACK READY**: v2 system can be deployed immediately if v3 encounters issues
- **EXPECTATION**: v3 should achieve ≥91% accuracy once prompt is updated for multi-platform support

**Edge Case Testing Focus:**
- **Misspellings**: "shacky" → "shakiness"
- **Abbreviations**: "BG", "CGM", "RNY", "PBH"  
- **Negations**: "NOT shaky", "NO longer experiencing"
- **Diagnostic confusion**: Late dumping vs PBH terminology
- **Privacy language**: "my procedure" vs explicit surgery mentions

## Project Structure & Data Architecture

### Organized File Structure
```
SIGNAL/
├── project_docs/                              # Documentation
│   ├── CLAUDE.md                             # This file - Claude guidance
│   └── ENRICHMENT_TEST_TRACKER.md            # Test tracking & issues
├── reference_schemas/                         # Static CSV references
│   ├── PBH_SIGNAL_NORMALIZATION_SCHEMA.csv   # Input format spec
│   ├── PBH_SIGNAL_ENRICHMENT_SCHEMA.csv      # Output field definitions
│   └── PBH_SIGNAL_DASHBOARD_FEATURES.csv     # Dashboard requirements
├── test_data/                                # Test cases
│   ├── reddit_example_1-11.json             # Reddit validation examples
├── enrichment_system/                        # Versioned systems
│   ├── v1/                                   # First stable version
│   ├── v2/                                   # Reddit production-ready (91% accuracy)
│   │   ├── normalization_schema_v2.csv      # Reddit test format schema
│   │   └── [v2 enrichment files]            # Dictionary, prompt, response format
│   └── v3/                                   # Multi-platform experimental
│       ├── normalization_schema_v3.json     # Unified Reddit+TikTok schema
│       └── [v3 enrichment files]            # Dictionary, prompt, response format
└── [Active Files - Root Level]              # Current working versions
    ├── PBH_SIGNAL_DICTIONARY.txt            # Dictionary (editable)
    ├── openai_assistant_system_prompt.md    # System prompt (editable)
    └── openai_assistant_response_format.json # JSON schema (editable)
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

## Recent Development Work (September 2024)

### Version 1 Enrichment System (Complete)
**Created:** `enrichment_system/v1/` with optimized baseline files

**Key Improvements:**
1. **Dictionary Taxonomy Alignment**: Updated all field references to match dictionary Categories/Labels structure
2. **Derived Fields Enhancement**: Optimized AI classifications (sentiment, emotions, intent, key_phrases, flags)
3. **Entity Extraction Clarity**: Strengthened deterministic Label extraction from dictionary Variations
4. **Schema Validation**: Ensured JSON response format aligns perfectly with prompt instructions
5. **Project Organization**: Implemented version control structure with clear separation of concerns

### Testing Workflow (Active Phase)
1. **Test Execution**: User runs Reddit examples through OpenAI Assistant
2. **Results Analysis**: Claude analyzes outputs vs expected results 
3. **Issue Identification**: Claude identifies specific extraction/classification problems
4. **System Optimization**: Claude recommends and executes fixes to dictionary/prompt/schema
5. **Progress Tracking**: Claude updates CSV tracker with test results and issues found
6. **Version Control**: Claude creates new versions (v2, v3, etc.) when major improvements achieved
7. **Iteration**: Repeat cycle until >90% test accuracy reached

### Claude's Testing Copilot Role
- **Immediate Response**: When user shares test results, analyze and recommend fixes
- **Hands-On Fixes**: Don't just suggest - actually implement the improvements
- **Data-Driven**: Use CSV tracker to identify patterns and prioritize fixes
- **Version Management**: Create new system versions when significant improvements made

### Version 2 Enrichment System (Production Ready)
**Status:** Complete and validated for Reddit-only deployment
**Location:** `enrichment_system/v2/`
**Accuracy:** 91% (10/11 test cases passing)

**v2 Key Achievements:**
- Sophisticated triangulation logic for relevance scoring
- Personal vs professional context detection
- Explicit exclusion rules (r/keto, r/diabetes)
- Production-ready for Reddit content enrichment

### Version 3 Multi-Platform System (Production Ready)
**Status:** Complete and validated for Reddit + TikTok deployment
**Location:** `enrichment_system/v3/`
**Schema:** `normalization_schema_v3.json` - unified Reddit + TikTok support

**v3 Testing Results (Complete - September 2024):**
✅ **Multi-Platform Validation**: 19 test cases (11 Reddit + 8 TikTok)
✅ **Reddit Performance**: 98.2% average accuracy (all 11 cases passing)  
✅ **TikTok Performance**: 97.9% average accuracy (all 8 cases passing)
✅ **Combined Performance**: 98.05% average accuracy - exceeds 90% threshold
✅ **Production Ready**: Both platforms validated for deployment

**v3 Key Achievements:**
1. **Multi-Platform Logic**: Successfully handles Reddit subreddits + TikTok hashtags
2. **Cross-Platform Consistency**: False positive prevention works identically on both platforms
3. **Edge Case Mastery**: Privacy language, diagnostic confusion, dual professional/personal contexts
4. **Schema Unification**: Clean v3 schema supports both platforms seamlessly
5. **Enhanced Intelligence**: Improved flag logic, emotion detection, and clinical reasoning

**Outstanding Issues (Minor):**
- **Audience Detection**: 1 case of dual professional/personal context misclassification (tiktok_example_8)
- **Company Extraction**: Minor gaps in inferring companies from medications (Amylyx from avexitide)

**v4 Enhancement Planning:**
**Next Phase:** Minor prompt optimizations and expanded test case coverage
**Focus Areas:**
1. **Audience Logic Refinement**: Improve dual professional/personal context detection
2. **Entity Linkage**: Strengthen medication→company inference rules  
3. **Additional Platforms**: Prepare for Facebook/Instagram expansion
4. **Edge Case Discovery**: Create new test scenarios based on real-world content patterns