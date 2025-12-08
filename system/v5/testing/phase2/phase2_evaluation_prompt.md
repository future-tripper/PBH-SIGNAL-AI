# Phase 2 Evaluation: Real-World Data Review

## Overview

Phase 2 validates the v5 enrichment system against real production data. Unlike Phase 1 (which compares against pre-defined expected outputs), Phase 2 requires evaluating whether the enrichment is **correct** based on analyzing the raw post content.

## Data Source

- **Input:** `SIGNAL_v5_real_enriched_data_CLEAN.csv`
- **Content:** Real posts from production with v5 enrichment applied
- **Columns:** Raw content (url, title, text) + all enrichment fields

## Evaluation Process

For each post, evaluate these fields against the raw content:

### Tier 1: Critical/Safety Fields (Must be correct)

| Field | How to Evaluate |
|-------|-----------------|
| `relevance_label` | Does post discuss PBH, bariatric hypoglycemia, or related symptoms in bariatric context? |
| `bariatric_context` | Are there explicit surgery references (VSG, RNY, gastric bypass, sleeve, "post-op", "WLS")? |
| `audience_label` | Who is the author? Patient ("I/my" + personal experience), HCP (clinic, professional), industry, media? |
| `flags` | Should adverse_event be flagged (avexitide + symptoms + causal language)? Crisis (self-harm)? Misattribution? |

### Tier 2: Core Product Fields

| Field | How to Evaluate |
|-------|-----------------|
| `sentiment_label` | What is the overall emotional tone? Positive, negative, neutral, or mixed? |
| `engagement_label` | Is the calculated engagement score correct? (likes + 2*comments + 3*shares) |

### Tier 3: Enhancement Fields (Track only)

| Field | How to Evaluate |
|-------|-----------------|
| `topics` | Are extracted topics mentioned in text? |
| `symptoms` | Are extracted symptoms actually described in post? |
| `treatments` | Are extracted treatments mentioned? |
| `emotions` | Do emotions match the tone of the post? |

## Evaluation Criteria

### relevance_label
- **relevant:** PBH explicitly mentioned OR (strong bariatric context + hypoglycemia/multiple symptoms)
- **borderline:** Weak bariatric context + symptoms OR ambiguous cases
- **not_relevant:** No bariatric context OR off-topic (weight loss celebration, diet tips without PBH)

### bariatric_context
- **strong:** Explicit surgery type (VSG, RNY, gastric bypass, sleeve, duodenal switch) OR known bariatric subreddit
- **weak:** Indirect references ("since my surgery", "post-op") without specific surgery type
- **none:** No surgery references at all

### audience_label
- **patient:** Personal experience markers ("I have", "my symptoms", "since my surgery")
- **hcp:** Professional context ("in clinic", "my patients", "we see cases")
- **industry:** Pharma/company content, trial recruitment
- **media:** News reporting, journalism
- **unknown:** Cannot determine

### flags
- **adverse_event:** ONLY if avexitide (or Amylyx trial drug) + actual symptoms + causal language ("after taking", "caused", "gave me")
- **crisis:** Self-harm language, severe psychological distress
- **possible_PBH_misattribution:** Strong bariatric context + hypoglycemia symptoms but NOT diagnosed as PBH

## Output Format

For each post, record in `phase2_test_results.csv`:

```csv
post_id,source,category,tier1_pass,tier2_pass,tier3_pass,overall_pass,critical_pass,flags_correct,relevance_correct,audience_correct,bariatric_context_correct,sentiment_correct,entity_extraction_quality,issues_found,recommended_fix
```

### Pass/Fail Logic
- **tier1_pass:** PASS if flags, relevance_label, audience_label, bariatric_context all correct
- **tier2_pass:** PASS if sentiment_label correct
- **critical_pass:** Same as tier1_pass
- **overall_pass:** PASS if all tiers pass

## Categorization

Categorize each post for pattern analysis:
- **relevant_pbh:** Clearly about PBH
- **relevant_symptoms:** Bariatric + hypoglycemia symptoms (potential PBH)
- **borderline:** Weak signals, ambiguous
- **not_relevant_bariatric:** Bariatric content but not PBH-related
- **not_relevant_other:** Off-topic entirely

## Success Criteria

Phase 2 passes when:
- **Tier 1 Pass Rate:** ≥90% (critical/safety fields)
- **No Critical Misses:** All adverse_event and crisis flags correct
- **Pattern Analysis:** No systematic issues identified

## Report Generation

After evaluation, use `../shared/generate_report.py` to create summary report (same format as Phase 1).
