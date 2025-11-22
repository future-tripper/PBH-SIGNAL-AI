# SIGNAL Reference Schemas - v5 Documentation

**Last Updated:** November 20, 2025
**Version:** 5.0 (Avexitide AE Reporting)

## Overview

This directory contains the reference CSV schemas for the SIGNAL platform enrichment system. These schemas define the data structure, field definitions, and enrichment logic used throughout the SIGNAL data pipeline (Fetching → Normalization → Enrichment → Storage).

## File Structure

```
reference_schemas/
├── README.md                                    # This file
├── AMX1013_PBH_SIGNAL_features_v5.csv          # Dashboard features specification (includes AE Reporting)
├── PBH_SIGNAL_DICTIONARY_v5.csv                # Entity extraction taxonomy (51 entries)
├── PBH_SIGNAL_NORMALIZATION_SCHEMA_v5.csv      # Input data structure (20 fields)
├── PBH_SIGNAL_ENRICHMENT_SCHEMA_v5.csv         # Output data structure (42 fields, enhanced AE criteria)
├── v3_archive/                                  # Archived v3 schemas (Reddit + TikTok only)
│   ├── PBH_SIGNAL_DICTIONARY.csv
│   ├── PBH_SIGNAL_ENRICHMENT_SCHEMA.csv
│   └── PBH_SIGNAL_NORMALIZATION_SCHEMA.csv
└── v4_archive/                                  # Archived v4 schemas (5-platform MVP)
    ├── PBH_SIGNAL_DICTIONARY_v4.txt
    ├── normalization_schema_v4.json
    ├── openai_assistant_response_format_v4.json
    ├── openai_assistant_system_prompt_v4.md
    └── README_v4_ARCHIVE.md
```

## v5 Changes Summary

### Adverse Event Detection Enhancement (v4 → v5)
- **v4**: Basic AE flag for any treatment ("treatment caused symptoms")
- **v5**: FDA-aligned avexitide-specific AE detection
  - 3-criteria rule: (1) avexitide product, (2) temporal/causal link, (3) symptoms present
  - Third-person reporting support ("My aunt...", "A patient...")
  - Explicit exclusions (hearsay, hypotheticals, suggestions, competitor drugs)
  - Symptom suppression in non-actual contexts

### Dashboard Features Update
- Added: **Adverse Event Reporting** module (row 6 in features CSV)
- Enables compliance/medical team to review flagged avexitide AEs
- Future v6: Alert/notification system for real-time monitoring

### Enrichment Schema Update
- Updated `flags` field documentation with v5 AE criteria
- No schema structure changes (flags array unchanged)

## v4 Changes Summary (Archived)

### Platform Coverage Enhancement
- **v3**: Reddit + TikTok (2 platforms)
- **v4**: Reddit + TikTok + Instagram + Facebook + Twitter* (5 platforms)
  - *Note: Twitter included but text content unavailable due to API restrictions

### Schema Enhancements

#### Normalization Schema (v3 → v4)
**Field Name Changes:**
- `timestamp` → `published_at` (standardized naming)
- `sentiment_raw` → `sentiment` (simplified)
- `permalink` field removed

**Nested Author Object:**
- OLD: Flat `author_handle` (string)
- NEW: Nested `author` object with 6 sub-fields:
  - `author.id` - Platform-specific author ID
  - `author.name` - Display name or full name
  - `author.handle` - Handle or username
  - `author.gender` - Gender (YouScan approximates for IG/FB/TikTok)
  - `author.age` - Age (YouScan approximates for IG/FB/TikTok)
  - `author.subscribers` - Follower/subscriber count

**New Fields:**
- `parent_source` - Hierarchical source category (e.g., "social" for multi-platform YouScan posts)
- `country` - ISO 3166-1 alpha-2 country code for geographic tracking

**Total Fields:** 20 (up from 14 in v3)

#### Enrichment Schema (v3 → v4)
**Passthrough Fields Added:**
- All 21 normalized fields now pass through to enrichment output
- Ensures complete data preservation throughout pipeline

**Total Fields:** 42 (21 passthrough + 21 derived, up from 21 derived-only in v3)

**Enhanced Documentation:**
- Added "Source" column distinguishing Passthrough vs Derived fields
- Added "Required" column specifying mandatory fields
- Documented enrichment logic in "Populate From / Rules" column

#### Dictionary (v3 → v4)
**Structure:** No changes to taxonomy structure (Category → Label → Variations → Exclude)

**Content:** Enhanced with production-validated patterns from real multi-platform data

**Total Entries:** 51 (unchanged from v3)
- audience_anchor: 2 entries
- companies: 5 entries
- conditions: 5 entries
- symptoms: 11 entries
- treatments: 10 entries
- topics: 18 entries

## File Descriptions

### 1. PBH_SIGNAL_DICTIONARY_v4.csv
**Purpose:** Entity extraction taxonomy for enrichment

**Columns:**
- `Entry_ID` - Unique identifier (001-051)
- `Category` - Target output field (audience_anchor, companies, conditions, symptoms, treatments, topics)
- `Label` - Exact term to extract and store (e.g., "PBH", "Amylyx", "shakiness", "avexitide")
- `Variations` - Pattern examples for AI recognition (pipe-delimited, not exhaustive)
- `Exclude` - Negative context terms that suppress extraction (e.g., "novo restaurant" for Novo Nordisk)
- `Note` - Additional context or description

**Usage:** Used by OpenAI enrichment prompt to identify and extract entities from social media text

### 2. PBH_SIGNAL_NORMALIZATION_SCHEMA_v4.csv
**Purpose:** Defines the standardized input format for enrichment

**Columns:**
- `Field` - Field name (uses dot notation for nested objects)
- `Type` - Data type (string, integer, datetime, etc.)
- `Description` - Field purpose and usage notes
- `Example` - Sample value
- `Required` - TRUE if mandatory, FALSE if optional

**Key Features:**
- 20 fields total (9 top-level + 6 author sub-fields + 3 metrics sub-fields + 2 other)
- Nested structures: `author.*` (6 fields), `metrics.*` (3 fields)
- Platform-agnostic design supporting all 5 MVP sources

**Field Groups:**
- **Source Info:** source, source_id, url, title, text, parent_source, subsource
- **Author Info:** author.id, author.name, author.handle, author.gender, author.age, author.subscribers
- **Metadata:** country, language, published_at, sentiment
- **Metrics:** metrics.likes, metrics.comments, metrics.shares

### 3. PBH_SIGNAL_ENRICHMENT_SCHEMA_v4.csv
**Purpose:** Defines the complete output format after enrichment (input + enrichment)

**Columns:**
- `Field` - Field name (uses dot notation for nested objects)
- `Type` - Data type (string, array, enum, number, etc.)
- `Allowed/Format` - Constraints (enums, array max items, ranges)
- `Source` - "Passthrough" (from normalization) or "Derived" (from enrichment)
- `Populate From / Rules` - Logic for how field is populated
- `Required` - TRUE if mandatory, FALSE if optional
- `Notes` - Additional context

**Structure:** 42 fields total
- **Passthrough (21 fields):** All normalization fields preserved
- **Derived (21 fields):** Enrichment-generated fields

**Enrichment Logic Documented:**

*Dictionary-Based Extraction:*
- `topics` - Category=topics matches
- `symptoms` - Category=symptoms matches
- `treatments` - Category=treatments matches
- `conditions` - Category=conditions matches
- `companies` - Category=companies matches

*Calculated Metrics:*
- `engagement_score` - Formula: `likes + (2 × comments) + (3 × shares)`
- `engagement_label` - Thresholds: high (≥20), med (10-19), low (<10)

*Relevance Determination:*
- `bariatric_context` - Logic: strong if topics includes bariatric_surgery OR subsource matches bariatric communities; weak if text contains indirect references ("since my surgery", "post-op", etc.); else none
- `relevance_label` - Triangulation: relevant if (conditions contains "PBH") OR (bariatric_context=strong AND (conditions contains "hypoglycemia"/"reactive_hypoglycemia" OR symptoms.length ≥2)); borderline if (bariatric_context=weak AND conditions/symptoms present); else not_relevant
- `relevance_confidence` - Model confidence score (0.0-1.0)
- `relevance_reason` - Text explanation for QA

*Audience Classification:*
- `audience_label` - Dictionary anchor patterns: patient if matches "patient_anchor" patterns ("i have", "my symptoms", "since my surgery"); hcp if matches "hcp_anchor" patterns ("my patient", "in clinic", "we see patients"); industry/media/unknown for other contexts
- `audience_confidence` - Model confidence score (0.0-1.0)

*Theme Mapping:*
- `themes` - Derived roll-up: Symptoms (if symptoms.length>0), Treatments (if treatments.length>0), Conditions/Diagnosis (if conditions.length>0), Bariatric Surgery (if topics includes bariatric_surgery), Access & Coverage (if topics includes access_coverage), Diagnostics (if topics includes diagnostics_monitoring), Diet (if topics includes dietary_modification), Care Settings (if topics includes care_settings)

*Sentiment & Emotion:*
- `sentiment_label` - Base classification with PBH-specific adjustments
- `sentiment_confidence` - Confidence ranges: 0.8-1.0 (clear), 0.6-0.7 (moderate), 0.4-0.5 (subtle)
- `emotions` - Multi-select from [anger, fear, sadness, joy, frustration, anxiety, hope, relief] with clear textual evidence required

*Content Analysis:*
- `key_phrases` - 5-10 medically relevant phrases using 5-category strategy: Symptom+Context, Treatment+Outcome, Timing Patterns, Diagnostic Terms, Medical Conditions
- `intent` - Multi-select from [seeking_advice, sharing_experience, giving_advice, news, venting] using linguistic patterns

*Flags:*
- `flags` - Multi-select: possible_PBH_misattribution (bariatric_context=strong + hypoglycemia but NOT PBH + ≥2 symptoms), crisis (self-harm language), adverse_event (treatment CAUSED symptoms)

*QA Tracking:*
- `debug_matches` - Array of Entry_IDs from dictionary for all extracted Labels (e.g., "conditions_PBH_008", "treatments_avexitide_024")

### 4. AMX1013_PBH_SIGNAL_features_v4.csv
**Purpose:** Dashboard feature requirements and visualization specifications

**Content:** Defines 6 dashboard cards:
1. Trends (Volume + Velocity)
2. Topics & Narratives
3. High Impact Posts
4. Market Share of Voice (SOV)
5. Chatbot Module
6. Bi-Monthly Report Archive

**Usage:** Requirements document for frontend development, not part of data pipeline

## Implementation Notes

### Data Pipeline Flow
1. **FETCHING** - Collect raw data from platforms (YouScan API + Reddit OAuth API)
2. **NORMALIZING** - Transform to v4 normalization schema (20 fields)
3. **ENRICHING** - Apply dictionary matching + OpenAI GPT-4o enrichment (42 fields total)
4. **STORING** - Load to Supabase + index to Algolia for dashboard/chatbot

### Key Business Rules

**Engagement Scoring:**
```
engagement_score = likes + (2 * comments) + (3 * shares)
engagement_label = "high" if score ≥ 20
                 = "med"  if score 10-19
                 = "low"  if score < 10
```

**Relevance Triangulation:**
```
bariatric_context = "strong" if topics includes bariatric_surgery OR subsource matches bariatric communities
                  = "weak"   if text contains "since my surgery", "post-op", "after my bypass/sleeve"
                  = "none"   otherwise

relevance_label = "relevant"     if conditions contains "PBH"
                                 OR (bariatric_context="strong" AND (conditions contains hypoglycemia OR symptoms.length ≥ 2))
                = "borderline"   if bariatric_context="weak" AND (conditions contains hypoglycemia OR symptoms.length ≥ 1)
                = "not_relevant" otherwise
```

**Audience Detection:**
- Uses dictionary audience_anchor Labels (patient_anchor, hcp_anchor)
- patient: Personal experience markers ("i have", "my symptoms", "since my surgery")
- hcp: Professional context markers ("my patient", "in clinic", "we see patients")

**Theme Derivation:**
- Presence-based mapping from enrichment tags (multi-label allowed)
- Symptoms theme: symptoms.length > 0
- Treatments theme: treatments.length > 0
- Bariatric Surgery theme: topics includes "bariatric_surgery"
- Access & Coverage theme: topics includes "access_coverage"
- Diagnostics theme: topics includes "diagnostics_monitoring"
- Diet theme: topics includes "dietary_modification"
- Care Settings theme: topics includes "care_settings"

### Platform-Specific Notes

**YouScan (Instagram, Facebook, TikTok):**
- Provides `parent_source: "social"` for hierarchical tracking
- Approximates age and gender for demographic analysis (not available from native APIs)
- Subsource captures platform-specific identifiers (FB page, TikTok hashtag)

**Reddit:**
- Direct OAuth API fetch (not through YouScan)
- Subsource captures subreddit name (e.g., "BariatricSurgery", "gastricsleeve")
- No age/gender data available

**Twitter:**
- Text content unavailable due to API restrictions
- Platform should be excluded from workflow (filter not functional)

### CSV Parsing Guidelines

**Nested Structures:**
- Use dot notation for nested objects in field names
- Example: `author.id`, `author.name`, `metrics.likes`
- Parse as nested JSON objects when implementing

**Array Fields:**
- Pipe-delimited (`|`) in dictionary Variations and Exclude columns
- Semicolon-delimited (`;`) in enrichment list fields (as specified in Type column)
- Max items specified in Allowed/Format column

**Null Handling:**
- Fields marked with `|null` type can be null
- Required=FALSE fields can be omitted or null
- Required=TRUE fields must always have values

## Version History

### v4.0 (November 2025) - 5-Platform MVP
- **Platform Expansion:** Added Instagram, Facebook, Twitter to existing Reddit + TikTok
- **Schema Enhancement:** Nested author object, geographic tracking, hierarchical source structure
- **Documentation:** Added enrichment logic, required column, source distinction
- **Archive:** Created v3_archive/ for previous schemas

### v3.0 (September 2025) - Multi-Platform Production
- **Platforms:** Reddit + TikTok (2 platforms)
- **Performance:** 98.05% accuracy (19/19 test cases passing)
- **Features:** Platform-agnostic relevance logic, enhanced false positive prevention

### v2.0 (August 2025) - Reddit-Optimized
- **Platforms:** Reddit only
- **Performance:** 91% accuracy (10/11 test cases passing)
- **Features:** Triangulation logic, personal vs professional context detection

### v1.0 (July 2025) - Baseline
- **Platforms:** Reddit only
- **Performance:** 80% accuracy (8/10 test cases passing)
- **Features:** Initial dictionary and prompt structure

## Support

For questions about these schemas or v4 implementation:
- Review enrichment system source files in `/enrichment_system/v4/`
- Consult `CLAUDE.md` in project root for implementation guidance
- Reference v4 test cases in `/enrichment_system/v4/test_data_v4/`

---

**Generated with Claude Code** | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
