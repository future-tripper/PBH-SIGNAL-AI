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

**Active Development:** Chatbot System Prompt (2025-12-10)

**v6.1 Enrichment:** ✅ DEPLOYED
- Tier 1: 100%, Tier 2: 83.7%
- Files: `system/v6/enrichment/openai_assistant_system_prompt_v6.1_with_dictionary.md` + `openai_assistant_response_format_v6.1.json`

**v7 Enrichment:** ✅ READY (for future deployment)
- Tier 1: 100%, Tier 2: 80.4%
- Key change: `audience_label` "patient" → "community" (captures caregivers)
- Files: `system/v7/enrichment/`
- Full details: `system/v7/V7_IMPLEMENTATION_PLAN.md`

**Chatbot:** IN PROGRESS
- Status: Setup complete, waiting for initial system prompt
- Files: `chatbot/`
- Full details: `chatbot/CHATBOT.md`

**Platforms:** 4-platform MVP (Reddit, TikTok, Facebook, Instagram)

## Project Structure & Data Architecture

### File Structure
```
PBH-SIGNAL-AI/
├── CLAUDE.md                                 # This file - project context
├── chatbot/                                  # IN PROGRESS - chatbot system
│   ├── CHATBOT.md                           # Status and iteration notes
│   ├── chatbot_system_prompt_v1.md          # Current prompt (TBD)
│   ├── testing/                             # Test prompts and issues
│   │   ├── test_prompts.md
│   │   └── ISSUES.md
│   └── archive/                             # Old prompt versions
├── reference_schemas/                        # Static CSV references (don't edit)
├── system/                                   # Enrichment system versions
│   ├── v5/                                  # Previous version (44 simulated test cases)
│   ├── v6/                                  # DEPLOYED - v6.1 is in production
│   │   ├── enrichment/
│   │   │   ├── openai_assistant_system_prompt_v6.1_with_dictionary.md  # ✅ DEPLOYED
│   │   │   └── openai_assistant_response_format_v6.1.json              # ✅ DEPLOYED
│   │   └── testing/                         # 46 real-world test cases
│   └── v7/                                  # READY - for future deployment
│       ├── V7_IMPLEMENTATION_PLAN.md        # Status, diffs, remaining issues
│       ├── enrichment/
│       │   ├── openai_assistant_system_prompt_v7_with_dictionary.md
│       │   └── openai_assistant_response_format_v7.json
│       └── testing/
└── [older versions archived]
```

### Active Development Files (v6.1)

**Deliverables for Dev Team:**
1. **Prompt:** `system/v6/enrichment/openai_assistant_system_prompt_v6.1_with_dictionary.md`
   - Includes embedded dictionary
   - Theme derivation guards
   - Expanded relevance logic for bariatric content

2. **Schema:** `system/v6/enrichment/openai_assistant_response_format_v6.1.json`
   - Enum constraints on entity arrays
   - `engagement_label`: "low", "medium", "high" (not "med")

3. **API Request Template:** `system/v6/enrichment/openai_api_request_template_v6.1.json`
   - Complete request payload with prompt + schema embedded
   - Ready for n8n/pipeline integration

### Model Configuration (v6.1)
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Model** | `gpt-4o` | OpenAI model |
| **Temperature** | `0.3` | Balances consistency with flexibility |
| **Response Format** | `json_schema` | Structured outputs with `strict: true` for enum enforcement |

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
- `high`: ≥20
- `medium`: 10-19 (note: use "medium" not "med")
- `low`: <10

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

## System Version History

| Version | Focus | Accuracy | Key Achievement |
|---------|-------|----------|-----------------|
| v1 | Baseline | 80% | Initial dictionary and prompt structure |
| v2 | Reddit-Optimized | 91% | Triangulation logic, exclusion rules |
| v3 | Multi-Platform | 98% | Reddit + TikTok, platform-agnostic relevance |
| v4 | Full MVP | - | 4 platforms, real production data, schema enhancements |
| v5 | Edge Cases | 93-97% | 44 test cases, AE detection, tier-based evaluation |
| **v6.1** | **Expanded Relevance** | **Tier1: 100%, Tier2: 83.7%** | **CURRENT - Real-world validation, broader relevance** |

**Note on Tiers:** Tier 1 = Critical/Safety fields (≥90% required). Tier 2 = Core product (≥80% required). Tier 3 = Enhancements (tracked but not blocking).

### v6/v6.1: Expanded Relevance Logic (Current)
- **Key Change:** Broader relevance criteria to capture more bariatric-related content
- **Problem Solved:** v5 marked 99%+ of posts as "not_relevant" because relevance required PBH/hypoglycemia
- **New Treatment Groups for Relevance:**
  - PBH_TREATMENTS: ["avexitide", "acarbose", "diazoxide", "octreotide"] - all trigger "relevant"
  - GLP1_TREATMENTS: ["semaglutide", "tirzepatide", "dulaglutide", "liraglutide", "exenatide"] - trigger "relevant" when combined with bariatric context
- **Updated Relevance Tiers:**
  - **relevant**: PBH conditions, PBH treatments (any), strong bariatric + 2+ PBH symptoms, strong bariatric + hypoglycemia condition, strong bariatric + GLP-1s
  - **borderline**: Strong bariatric context alone (general surgery discussions without PBH indicators)
  - **not_relevant**: No bariatric context, no relevant treatments, off-topic medical content
- **Dictionary Labels (v6.1)** - Valid extraction labels:
  - **symptoms**: shakiness, dizziness, sweating, hypoglycemia, brain_fog, tachycardia, fainting, nausea, seizures, vision_changes, weakness
  - **treatments**: avexitide, acarbose, semaglutide, tirzepatide, dulaglutide, liraglutide, exenatide, diazoxide, octreotide
  - **conditions**: PBH, reactive_hypoglycemia, hypoglycemia, late_dumping, idiopathic_postprandial_syndrome
  - **companies**: Amylyx, Novo_Nordisk, Eli_Lilly, AstraZeneca, Boehringer_Ingelheim
- **Testing:** 46 real posts from production pipeline validated against expected outputs

## v6.1 Testing Results (COMPLETE ✅)

**Final Results (2025-12-09):**
- Tier 1 (Critical): **100.0%** ✅ (target ≥90%)
- Tier 2 (Core): **83.7%** ✅ (target ≥80%)
- Test Cases: 46 real posts from production pipeline

**v6 vs v6.1 Key Differences:**
| Component | v6 | v6.1 (Current) |
|-----------|-----|------|
| engagement_label | `"low", "med", "high"` | `"low", "medium", "high"` |
| Entity arrays | No enum constraints | Enum constraints on topics, symptoms, treatments, conditions, companies |
| Prompt | Base with dictionary | + Theme derivation guard + dietary_modification expansion |

### v7 Backlog

Known issues documented for future development:

| Issue | Type | Priority |
|-------|------|----------|
| Rename "patient" to "community" for audience_label | Schema | High |
| Themes array allows duplicates | Schema | High |
| Hypoglycemia over-extraction from diabetes context | Prompt | Medium |
| "Dumping syndrome" vs "late_dumping" confusion | Prompt | Medium |
| Doctor visit under-extraction | Prompt | Medium |
| Emotion under-extraction (conservative inference) | Prompt | Medium |
| Engagement score calculation error | API Bug | High |

**Full details:** `system/v7/V7_BACKLOG.md`

### Next Steps

1. ✅ ~~v6.1 enrichment testing~~ - COMPLETE
2. 🔜 Chatbot system prompt development and testing
3. 🔜 Dashboard/front-end validation with enriched data

### How to Run Tests

```bash
cd system/v6/testing
python run_api_test.py --mode v6.1 --all   # Run enrichment via OpenAI API
python compare_v6_only.py                   # Compare results against expected outputs
```

### Key Files for Context Recovery

If starting a new session, read these files:
1. `CLAUDE.md` - This file (project context + current status)
2. `system/v7/V7_BACKLOG.md` - Known issues for v7 development
3. `system/v6/testing/expected_outputs/` - Ground truth for comparison
4. `system/v6/enrichment/` - Prompt and schema files (v6.1 is current)