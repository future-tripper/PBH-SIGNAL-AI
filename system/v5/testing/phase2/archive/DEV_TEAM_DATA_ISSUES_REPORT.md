# v5 Data Issues Report

**Date:** 2025-12-04
**Data Reviewed:** 172 rows → 51 usable (after removing unenriched/invalid rows)

---

## BOTTOM LINE

**We cannot test the enrichment system, dashboard, or chatbot until these issues are fixed.**

---

## Issue 1: Missing Schema Fields

The data export is missing required v5 fields.

| Missing Field | Why It Matters |
|---------------|----------------|
| `bariatric_context` | **Critical** - needed for relevance scoring |
| `engagement_score` | Dashboard ranking |
| `engagement_label` | Dashboard filtering |

**Why `bariatric_context` is critical:** PBH = hypoglycemia caused by bariatric surgery. Without this field, we can't distinguish actual PBH cases from general hypoglycemia chatter (diabetes, keto, fasting, etc.).

**Fix:** Update database/export to include all v5 fields. See `openai_assistant_response_format_v5.json`.

---

## Issue 2: No PBH-Relevant Data

**100% of the 51 posts are marked `not_relevant`.**

This means:
- We have zero PBH cases to validate
- Phase 2 testing is blocked

**Question:** Per the Nov 10 status review, non-relevant posts should be dropped before storage. Is this filter implemented? If not, this data could be reaching the dashboard/chatbot.

**Fix:** Send us data with `relevant` or `borderline` posts.

---

## Issue 3: Chatbot Quality is Limited by Data Quality

**What we can fix now (prompt work):**
- Reduce inconsistent responses (stricter logic, lower randomness)
- Add guardrails so chatbot only answers from retrieved data (not general knowledge)
- Require citations so we can verify source of answers

**What we can't fix until data is fixed:**
- Accurate PBH-specific answers (can't filter by `bariatric_context` if the field doesn't exist)
- Clean results (if non-relevant posts aren't filtered, chatbot will surface irrelevant content)
- Validation that our prompt rules work (can't test rules against fields/data that aren't there)

**Bottom line:** We can improve the prompt, but we can't prove it works until the data is fixed. We'd be polishing a car with no engine.

---

## WHAT WE NEED

| # | Action |
|---|--------|
| 1 | Confirm non-relevant posts are being filtered (not served to users) |
| 2 | Fix database/export to include all v5 schema fields |
| 3 | Send new data sample with PBH-relevant posts |

---

*Report generated 2025-12-04*
