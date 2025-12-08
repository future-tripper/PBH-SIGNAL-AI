# SIGNAL Reference Schemas - v6 Documentation

**Last Updated:** December 8, 2025
**Version:** 6.0 (Expanded Relevance Logic)

## Overview

This directory contains the reference CSV schemas for the SIGNAL platform enrichment system. These schemas define the data structure, field definitions, and enrichment logic used throughout the SIGNAL data pipeline (Fetching → Normalization → Enrichment → Storage).

## File Structure

```
reference_schemas/
├── README.md                                    # This file
├── AMX1013_PBH_SIGNAL_features_v6.csv          # Dashboard features specification
├── PBH_SIGNAL_DICTIONARY_v6.csv                # Entity extraction taxonomy (51 entries, updated variations)
├── PBH_SIGNAL_NORMALIZATION_SCHEMA_v6.csv      # Input data structure (20 fields)
├── PBH_SIGNAL_ENRICHMENT_SCHEMA_v6.csv         # Output data structure (42 fields, expanded relevance)
├── v3_archive/                                  # Archived v3 schemas (Reddit + TikTok only)
├── v4_archive/                                  # Archived v4 schemas (5-platform MVP)
└── v5_archive/                                  # Archived v5 schemas (comprehensive edge cases)
    ├── PBH_SIGNAL_DICTIONARY_v5.csv
    ├── PBH_SIGNAL_ENRICHMENT_SCHEMA_v5.3.4.csv
    ├── PBH_SIGNAL_NORMALIZATION_SCHEMA_v5.csv
    └── AMX1013_PBH_SIGNAL_features_v5.csv
```

## v6 Changes Summary

### Problem Solved
v5 marked 99%+ of posts as "not_relevant" because relevance required explicit PBH/hypoglycemia mentions. Real pipeline data showed:
- Only 6 out of 1,000 posts marked "relevant"
- 39 posts with clear bariatric surgery keywords marked "not_relevant"
- Posts mentioning PBH treatments (acarbose, diazoxide) not triggering relevance

### Key Changes (v5 → v6)

#### 1. Treatment Groups for Relevance
**NEW:** Treatments now organized into groups that affect relevance:

| Group | Treatments | Relevance Impact |
|-------|-----------|------------------|
| PBH_TREATMENTS | avexitide, acarbose, diazoxide, octreotide | Any mention → "relevant" |
| GLP1_TREATMENTS | semaglutide, tirzepatide, dulaglutide, liraglutide, exenatide | With bariatric context → "relevant" |

**v5:** Only avexitide triggered "relevant"
**v6:** All PBH treatments trigger "relevant"

#### 2. Expanded Relevance Tiers

**RELEVANT (keep and prioritize):**
- PBH condition mentioned
- ANY PBH_TREATMENTS mentioned (was: only avexitide)
- Strong bariatric context + ≥2 symptoms
- Strong bariatric context + hypoglycemia/reactive_hypoglycemia
- Strong bariatric context + GLP1_TREATMENTS (NEW)

**BORDERLINE (keep for context):**
- Strong bariatric context WITHOUT PBH indicators (NEW - was "not_relevant")
- Weak context + PBH treatments + ≥2 symptoms
- Weak context + ≥3 symptoms

**NOT_RELEVANT (filter out):**
- No bariatric context AND no relevant treatments
- Off-topic medical content (dermatology, respiratory, etc.)

#### 3. Dictionary Updates
- Added "acrobose" and "acarobose" misspellings to acarbose variations (found in real data)
- Updated treatment notes to indicate group membership (PBH_TREATMENTS vs GLP1_TREATMENTS)

### Expected Impact

| Metric | v5 | v6 (Expected) |
|--------|-----|---------------|
| Posts with bariatric context → relevant/borderline | 5 | ~53 |
| Posts with PBH treatments → relevant | 0 | ~1-5 |
| False negatives (bariatric posts marked not_relevant) | 39 | 0 |

## File Descriptions

### 1. PBH_SIGNAL_DICTIONARY_v6.csv
**Purpose:** Entity extraction taxonomy for enrichment

**Columns:**
- `Entry_ID` - Unique identifier (001-051)
- `Category` - Target output field (audience_anchor, companies, conditions, symptoms, treatments, topics)
- `Label` - Exact term to extract and store
- `Variations` - Pattern examples for AI recognition (pipe-delimited)
- `Exclude` - Negative context terms that suppress extraction
- `Note` - Additional context (includes treatment group membership for v6)

**v6 Changes:**
- Entry 025 (acarbose): Added "acrobose | acarobose" to Variations
- Treatment entries: Updated notes to indicate PBH_TREATMENTS vs GLP1_TREATMENTS group

### 2. PBH_SIGNAL_NORMALIZATION_SCHEMA_v6.csv
**Purpose:** Standardized input format for enrichment

**No changes from v5** - 20 fields total

### 3. PBH_SIGNAL_ENRICHMENT_SCHEMA_v6.csv
**Purpose:** Complete output format after enrichment

**v6 Changes:**
- `relevance_label` field: Updated rules with treatment groups and expanded borderline criteria
- `debug_matches` field: References PBH_SIGNAL_DICTIONARY_v6.csv

### 4. AMX1013_PBH_SIGNAL_features_v6.csv
**Purpose:** Dashboard feature requirements

**No changes from v5** - 6 dashboard cards

## Key Business Rules (v6)

### Relevance Triangulation (UPDATED)

```
# Treatment Groups
PBH_TREATMENTS = [avexitide, acarbose, diazoxide, octreotide]
GLP1_TREATMENTS = [semaglutide, tirzepatide, dulaglutide, liraglutide, exenatide]

# Bariatric Context
bariatric_context = "strong" if:
    - topics includes "bariatric_surgery" OR
    - conditions includes "PBH" or "late_dumping" OR
    - subsource matches bariatric communities
bariatric_context = "weak" if:
    - text contains "since my surgery", "post-op", etc.
bariatric_context = "none" otherwise

# Relevance Label (v6 EXPANDED)
relevance_label = "relevant" if:
    - conditions contains "PBH" OR
    - treatments contains ANY PBH_TREATMENTS OR
    - (bariatric_context="strong" AND symptoms.length ≥ 2) OR
    - (bariatric_context="strong" AND conditions contains hypoglycemia) OR
    - (bariatric_context="strong" AND treatments contains ANY GLP1_TREATMENTS)

relevance_label = "borderline" if:
    - bariatric_context="strong" WITHOUT PBH indicators (general bariatric content) OR
    - (bariatric_context="weak" AND treatments contains PBH_TREATMENTS AND symptoms.length ≥ 2) OR
    - (bariatric_context="weak" AND symptoms.length ≥ 3)

relevance_label = "not_relevant" if:
    - bariatric_context="none" AND no relevant treatments OR
    - off-topic medical content
```

### Engagement Scoring (unchanged)
```
engagement_score = likes + (2 * comments) + (3 * shares)
engagement_label = "high" if score ≥ 20
                 = "med"  if score 10-19
                 = "low"  if score < 10
```

### Audience Detection (unchanged)
- Uses dictionary audience_anchor Labels
- patient: Personal experience markers
- hcp: Professional context markers

## Version History

### v6.0 (December 2025) - Expanded Relevance Logic
- **Problem:** v5 marked 99%+ of posts as not_relevant
- **Solution:** Expanded relevance to capture bariatric content
- **Key Changes:**
  - All PBH treatments trigger "relevant" (not just avexitide)
  - Bariatric context alone → "borderline" (was "not_relevant")
  - GLP-1s + bariatric context → "relevant"
  - Added misspelling variations (acrobose, acarobose)

### v5.0 (November 2025) - Comprehensive Edge Cases
- **Test Coverage:** 44 test cases across 6 categories
- **Performance:** Tier 1 93.2%, Tier 2 97.7%
- **Features:** Event-based AE detection, enhanced flag logic

### v4.0 (November 2025) - 5-Platform MVP
- **Platform Expansion:** Reddit, TikTok, Instagram, Facebook, Twitter
- **Schema Enhancement:** Nested author object, geographic tracking

### v3.0 (September 2025) - Multi-Platform Production
- **Platforms:** Reddit + TikTok
- **Performance:** 98.05% accuracy

### v2.0 (August 2025) - Reddit-Optimized
- **Performance:** 91% accuracy
- **Features:** Triangulation logic

### v1.0 (July 2025) - Baseline
- **Performance:** 80% accuracy

## Support

For questions about these schemas or v6 implementation:
- Review enrichment system source files in `/system/v6/enrichment/`
- Consult `CLAUDE.md` in project root for implementation guidance
- Reference test data in `/system/v5/testing/phase2/` for real-world validation

---

**Generated with Claude Code** | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
