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

**Ready for Testing:** v4 Full MVP Platform Coverage with Enhanced Schema
- **Platforms:** 5-platform MVP (Reddit, TikTok, Facebook, Instagram, Twitter*)
- **Schema Enhancement:** Nested author data, demographics, geographic tracking
- **Real Data Sources:** 14 production test cases from actual MVP platforms
- **Testing Phase:** Manual validation of enrichment accuracy across all platforms
- **Previous:** v3 Multi-Platform (98.05% accuracy, Reddit + TikTok only)

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
├── enrichment_system/                        # Versioned systems
│   ├── v1/                                  # Baseline (80% accuracy)
│   ├── v2/                                  # Reddit-only (91% accuracy)
│   ├── v3/                                  # Multi-platform (98% accuracy)
│   │   ├── normalization_schema_v3.json    # Unified schema
│   │   ├── test_data_v3/                   # 19 test cases
│   │   └── [system files]                  # Dictionary, prompt, schema
│   └── v4/                                  # 5-platform MVP (in development)
│       ├── normalization_schema_v4.json    # Enhanced schema with demographics
│       ├── test_data_v4/                   # 14 real MVP test cases
│       └── [system files]                  # Dictionary, prompt, schema
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

## Testing Protocol (v4)

### Manual Validation Process
1. **Case Selection:** Test all 14 production examples (3 Reddit, 3 TikTok, 3 Facebook, 3 Instagram, 2 Twitter)
2. **Expected Output:** Generate correct enrichment using v4 system prompt + dictionary + response format
3. **Actual Testing:** Run through OpenAI Assistant API with v4 configuration
4. **Scoring:** Compare expected vs actual results field-by-field
5. **Documentation:** Record results in `project_docs/ENRICHMENT_TEST_RESULTS.csv`

### Test Coverage Goals
- **Platform Diversity:** Validate all 5 MVP platforms including new Facebook/Instagram
- **Schema Validation:** Ensure enhanced v4 schema fields (author, country, parent_source) work correctly
- **Edge Cases:** Twitter null text handling, clinical trial content, multi-platform relevance logic
- **Accuracy Target:** ≥98% to match or exceed v3 performance

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

### v4: Full MVP Platform Coverage (Ready for Testing)
- **Platforms:** 5-platform MVP (Reddit, TikTok, Facebook, Instagram, Twitter*)
- **Test Cases:** 14 real production examples from actual data sources
- **Schema Enhancement:**
  - Nested author object with demographics (gender, age, subscribers)
  - Geographic tracking (country codes)
  - Hierarchical content structure (parent_source, subsource)
  - Platform-specific metrics handling
- **Key Limitations:** Twitter text content unavailable due to API restrictions
- **Real Clinical Data:** Facebook examples include actual Amylyx PBH trial recruitment
- **Testing Approach:** Manual case-by-case validation against expected enrichment outputs
- **Success Target:** Maintain or exceed v3's 98% accuracy across expanded platform coverage