# Algolia Search Configuration for SIGNAL Chatbot

This document contains the configuration text for the Algolia search tool.

---

## Tool Description (Copy to Algolia Config UI)

**Character limit: 200**

```
PBH social posts (all relevant/borderline). Use facet_filters: symptoms, conditions, treatments, emotions, audience_label, topics, engagement_label, bariatric_context. Example: ["emotions:frustration"]
```

(Exactly 200 characters)

---

## Key Context

**Database contents (once enrichment is fixed):**
- ALL posts are `relevant` or `borderline` to PBH
- No need to filter by `relevance_label`
- Filter by the attributes users ask about

**Available filter fields:**

| Field | Values |
|-------|--------|
| symptoms | shakiness, dizziness, sweating, hypoglycemia, brain_fog, tachycardia, fainting, nausea, seizures, vision_changes, weakness |
| conditions | PBH, reactive_hypoglycemia, late_dumping, hypoglycemia, idiopathic_postprandial_syndrome |
| treatments | avexitide, acarbose, diazoxide, octreotide, semaglutide, tirzepatide, dulaglutide, liraglutide, exenatide |
| topics | bariatric_surgery, diagnostics_monitoring, dietary_modification, doctor_visit, surgery_complications, clinical_trial, quality_of_life, access_coverage |
| emotions | anger, fear, sadness, joy, frustration, anxiety, hope, relief |
| audience_label | patient, hcp, industry, media, unknown |
| sentiment_label | positive, negative, neutral, mixed |
| engagement_label | high, medium, low |
| bariatric_context | strong, weak, none |
| source | reddit.com, tiktok.com, facebook.com, instagram.com |

---

## facet_filters Syntax

### AND conditions (all must match)
```json
{"facet_filters": ["audience_label:patient", "emotions:frustration"]}
```

### OR conditions (any can match)
```json
{"facet_filters": [["symptoms:shakiness", "symptoms:dizziness", "symptoms:hypoglycemia"]]}
```

### Combined AND + OR
```json
{"facet_filters": [["symptoms:shakiness", "symptoms:dizziness"], "audience_label:patient"]}
```

---

## Query Examples

| User Question | facet_filters |
|---------------|---------------|
| "What language about crashes?" | `[["symptoms:shakiness", "symptoms:dizziness", "symptoms:hypoglycemia"]]` |
| "Are people frustrated?" | `["emotions:frustration"]` |
| "Undiagnosed PBH?" | `[["conditions:reactive_hypoglycemia", "conditions:late_dumping"]]` |
| "What are HCPs saying?" | `["audience_label:hcp"]` |
| "High engagement posts" | `["engagement_label:high"]` |
| "Acarbose discussions" | `["treatments:acarbose"]` |
| "Doctor visit posts" | `["topics:doctor_visit"]` |

**Use `number_of_results: 30-50` for pattern analysis.**
