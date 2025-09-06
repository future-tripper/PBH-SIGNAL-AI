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

**Production Ready:** v3 Multi-Platform system validated (98.05% accuracy on 19 test cases)
- **Platforms:** Reddit + TikTok fully supported
- **Test Results:** Tracked in `project_docs/ENRICHMENT_TEST_RESULTS.csv`
- **Next Phase:** v4 minor optimizations and expanded platform support (Facebook/Instagram)

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
│   └── v3/                                  # Multi-platform (98% accuracy)
│       ├── normalization_schema_v3.json    # Unified schema
│       ├── test_data_v3/                   # 19 test cases
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

### v4: Future Enhancements (Planned)
- Facebook/Instagram support
- Enhanced entity linkage (medication→company)
- Expanded test coverage
- Minor prompt optimizations