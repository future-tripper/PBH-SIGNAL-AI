# PBH SIGNAL v5 Testing Plan

**Master document for Dev Team and TCD Team validation workflow**

---

# THE PLAN: Three-Phase Testing

## What This Is
Automated validation of v5 enrichment system (AI that analyzes social media posts about PBH) using 44 test cases with known correct outputs.

**Goal:** Confirm ≥90% accuracy on critical safety fields (Tier 1) and ≥80% on core product fields (Tier 2) before production deployment.

---

## Phase 1: AI-Assisted Test Validation (Dev Team)

**WHO:** Dev team with enrichment pipeline already running
**WHEN:** Immediately after receiving this package
**TIME:** ~30-60 minutes (run tests, use Claude Code for comparison, review results)

### Prerequisites

**You need:**
- Enrichment pipeline configured with v5 system (see Step 0 above)
- Access to Claude Code or similar AI coding assistant
- 44 test input files (in `../enrichment-test-data-v5/` organized by category)

**Files you'll use:**
- `phase1_claude_prompt.md` - Detailed instructions for Claude Code
- `phase1_test_results.csv` - Where results will be tracked
- `CLAUDE.md` - Project context for AI assistant

---

### Internal Testing Results (For Context)

We've completed initial internal testing using Chat Completions API with 44 test cases:

**Results (Tier-Based):**
- **Tier 1 (Critical/Safety):** 70.5% — Below 90% threshold, needs improvement
- **Tier 2 (Core Product):** 81.8% — Above 80% target ✓
- **Tier 3 (Enhancements):** 20.5% — Tracking only (subjective fields)

**Key Takeaways:**
- **Root cause of 70.5% Tier 1 result:** `bariatric_context` field at 84% accuracy (needs 90%+)
  - This field is CORE to product functionality - determines if post is PBH-relevant
  - Other critical fields performing well: flags 91%, relevance 91%, audience 97.7%
  - Fixing bariatric_context alone would bring Tier 1 to ~90%+
- **Primary issue:** Not consistently recognizing PBH mentions as "strong" bariatric context
- **Secondary issues:** Flag logic edge cases, third-person narratives
- More comprehensive testing recommended before production deployment

See `completed_tests/test1_20251121/` for detailed analysis.

---

### Step-by-Step Process

#### Step 0: Configure v5 Enrichment System ⚠️ **DO THIS FIRST**

**Before running any tests, configure your enrichment pipeline with v5 system files.**

##### Required Configuration (n8n or API)

**Model Settings:**
- **Model:** `gpt-4o-2024-08-06`
- **Temperature:** `0.3` (balanced for consistency + nuance)

**System Files (from `../enrichment/` folder):**

**1. System Prompt:**
- File: `openai_assistant_system_prompt_v5.md`
- Where: Set as system message in your API call
- Content: Complete prompt instructions (~315 lines)
- **Note:** Updated with Adverse Event detection logic

**2. Schema Update:**
- **Add a 'flags' field** to your existing enrichment schema/database
- Type: Array of strings
- Purpose: Captures adverse event flags and other critical alerts
- Example: `"flags": ["adverse_event"]` or `"flags": []`
- Note: This field is required to capture Adverse Event detections from the updated prompt
- **Reference:** For complete v5 schema structure, see `../enrichment/openai_assistant_response_format_v5_wrapped.json`

**3. Dictionary (File Search Tool):** Strongly Recommended
- File: `PBH_SIGNAL_DICTIONARY_v5.txt`
- **Recommended approach:** Attach as File Search tool if your platform supports it
- **Alternative:** If File Search is not available, embedding the dictionary in the system prompt is acceptable
- Note: The system prompt references "File Search" for dictionary lookups, but will work with either approach

**Configuration checklist:**
- [ ] Model set to `gpt-4o-2024-08-06`
- [ ] Temperature set to `0.3`
- [ ] System prompt loaded from `openai_assistant_system_prompt_v5.md` (includes AE detection logic)
- [ ] 'flags' field added to your enrichment schema/database
- [ ] Dictionary attached as File Search tool (recommended) or embedded in prompt (alternative)

**Verify configuration:**
Test with one sample input. Check that:
- Output includes the 'flags' field
- Entity extraction works (symptoms, treatments, etc. captured)
- Adverse event posts correctly populate the flags array

#### 1. Run Tests Through Your Pipeline (5-10 min)

**Feed test inputs through your enrichment system:**

1. Locate test input files in `../enrichment-test-data-v5/`:
   - `ae-test-cases/` (12 JSON files)
   - `platform-coverage/` (8 JSON files)
   - `edge-cases/` (8 JSON files)
   - `dictionary-tests/` (6 JSON files)
   - `classification-tests/` (6 JSON files)
   - `flag-tests/` (4 JSON files)

2. Run each test input through your enrichment pipeline
   - Use v5 system prompt from `../enrichment/openai_assistant_system_prompt_v5.md`
   - Ensure your output schema includes the 'flags' field
   - Generate enriched JSON output for each test

3. Save outputs to `actual_outputs/` folder:
   - Name format: `{test_name}_actual.json`
   - Examples: `ae_test_1_actual.json`, `platform_reddit_1_actual.json`
   - Should have 44 files total when complete

**Tip:** If your pipeline can batch process, run all 44 at once. Otherwise, process category by category.

#### 2. Use Claude Code (or similar) for Comparison (15-30 min)

**Open your AI assistant with project context:**

1. Open Claude Code (or similar AI coding assistant) in this project directory
2. Ensure `CLAUDE.md` is available for context (provides v5 system knowledge)
3. Load the comparison prompt: `phase1_claude_prompt.md`

**Give Claude Code this task:**
```
Please follow the instructions in phase1_claude_prompt.md to:
1. Compare all actual outputs in actual_outputs/ with expected outputs in ../enrichment-test-data-v5/expected-outputs/
2. Populate phase1_test_results.csv with detailed results for each test
3. Identify failure patterns and recommend fixes
4. Generate a summary report
```

**Claude Code will:**
- Compare 44 test cases field-by-field
- Fill in `phase1_test_results.csv` with Pass/Fail per test and per component
- Document Key_Issues and Recommended_Fixes for each failure
- Identify patterns (e.g., "All AE tests failing on causal language")
- Suggest specific fixes with file/section references

#### 3. Review Results (10-15 min)

**Open `phase1_test_results.csv` and check:**

**Overall Metrics:**
- **Tier 1 (Critical/Safety) Pass Rate:** How many tests passed critical fields? (Target: ≥90%)
  - Critical fields: flags, relevance_label, audience_label, bariatric_context
- **Tier 2 (Core Product) Pass Rate:** How many tests passed core fields? (Target: ≥80%)
  - Core fields: sentiment_label, engagement_label
- **Tier 3 (Enhancements) Pass Rate:** How many tests passed enhancement fields? (Tracking only)
  - Enhancement fields: themes, emotions, intent (subjective)
- **Failure Patterns:** Are failures clustered (same category? same field?)

**Component Breakdown:**
- Dictionary_Extraction: Are entities being captured correctly?
- Relevance_Logic: Is relevance_label classification working?
- Sentiment_Analysis: Is sentiment + emotions detection accurate?
- Audience_Detection: Is audience_label correct for patients vs HCPs?
- AE_Flagging: Are adverse_event flags present when expected? ⚠️ CRITICAL
- Crisis_Detection: Are crisis flags present when expected? ⚠️ CRITICAL

**Read Claude's Diagnosis:**
- Review "Key_Issues" column - what went wrong in plain English
- Review "Recommended_Fixes" column - specific actionable fixes
- Review "Next_Actions" column - what to do next

### Success Criteria (Tiered Approach):

**Tier 1 (Critical/Safety) - REQUIRED for Production:**
- ✅ **Pass Rate:** ≥90% on critical fields (flags, relevance_label, audience_label, bariatric_context)
- ✅ **Patient Safety:** All AE flagging + crisis detection working correctly

**Tier 2 (Core Product) - Target for Production:**
- ✅ **Pass Rate:** ≥80% on core product fields (sentiment_label, engagement_label)

**Tier 3 (Enhancements) - Track & Improve:**
- 📊 **Track trends:** Monitor themes, emotions, intent accuracy (subjective fields)
- No hard threshold - these are nice-to-have enhancements

**Why Tiers?** Different fields serve different purposes. Patient safety (Tier 1) requires highest accuracy. Subjective enhancements (Tier 3) provide insights but aren't critical for core product value.

### If Tests Pass (≥90%): **Report to TCD:**

Email or Teams:
```
Subject: Phase 1 PASS - Ready for Phase 2

Phase 1 AI-Assisted Testing Complete ✅

RESULTS (Tier-Based):
- Tier 1 (Critical/Safety): 95% (42/44) ✅ Target: ≥90%
- Tier 2 (Core Product): 93% (41/44) ✅ Target: ≥80%
- Tier 3 (Enhancements): 75% (33/44) 📊 Tracking only

KEY METRICS:
- Patient Safety: All AE flagging + crisis detection working correctly ✅
- Core filtering: relevance_label, audience_label highly accurate
- Areas for improvement: themes consistency (subjective field)

ITERATIONS:
- Initial run: Tier 1 at 88% (below threshold)
- Fixed bariatric_context detection logic
- Re-ran tests: Tier 1 at 95% ✅

NEXT STEP:
Ready for Phase 2 - real sample data review

Attached: phase1_test_results.csv
```

**→ Move to Phase 2**

### If Tests Fail (Tier 1 <90% or Tier 2 <80%):

**Iterate with Claude Code:**

#### Step 1: Review Recommended Fixes

Claude Code has identified issues and suggested fixes in the CSV. Common patterns:

**Dictionary Issues:**
- Missing terms or variations
- Fix: Add entries to `../enrichment/PBH_SIGNAL_DICTIONARY_v5.txt`
- Example: "Add 'shakiness' variations: shaky|trembling|jittery"

**Prompt Issues:**
- Unclear logic or criteria
- Fix: Update `../enrichment/openai_assistant_system_prompt_v5.md`
- Example: "Emphasize AE causal language detection in adverse_event criteria"

**Schema Issues:**
- Field constraints too strict/loose
- Fix: Update `../enrichment/openai_assistant_response_format_v5.json`
- Example: "Make emotions array minItems: 0 (not required)"

#### Step 2: Implement Fixes

With Claude Code's help:
1. Open the recommended file (dictionary, prompt, or schema)
2. Make the suggested changes
3. Review with Claude to ensure fix is correct
4. Save changes

#### Step 3: Re-run Tests

1. Re-run the failed tests (or all 44) through your pipeline
2. Save new outputs to `actual_outputs/` (overwrite previous)
3. Ask Claude Code to re-compare and update CSV
4. Check if pass rate improved

#### Step 4: Repeat Until ≥95%

Continue iterating:
- Review → Fix → Test → Review
- Track iterations in CSV (add notes about what was fixed)
- Most systems converge in 2-3 iterations

#### Step 5: Report to TCD

---

## Phase 2: Real Sample Validation (TCD Team)

**WHO:** TCD team (Joe's team)
**WHEN:** After Phase 1 passes
**TIME:** 1-2 hours for sample collection + review

### What TCD Team Requests from Devs:
**Send real production samples** (email/Teams):
- **CSV format** (enriched posts with all fields visible in spreadsheet)
- 20-50 diverse posts with enrichment results:
  - Patient posts (personal stories, questions)
  - HCP content (clinical info, advice)
  - Off-topic posts (in bariatric forums but not about PBH)
  - Edge cases (unusual content, sarcasm, etc.)

**Provide real enriched files in CSV Format (readable for TCD non-devs):**
- Include key enrichment fields: source, text, relevance_label, audience_label, sentiment_label, emotions, themes, topics, symptoms, treatments, flags, etc.
- Easy to open in Excel/Google Sheets for review

### What TCD Team Does:
2. **Validate quality** on real-world data
3. **Document any issues** in phase2_review_template.csv

### Outcomes:
- ✅ **High confidence** → Approve for production
- ⚠️ **Issues found** → Update v5 system → Re-test

### TCD Review Process: Step-by-Step

#### 1. What to Review (All Enrichment Fields)

For each post in the CSV, check these enrichment fields:

**Relevance (Is this about PBH?):**
- `relevance_label`: Should be "relevant" if post mentions PBH or bariatric hypoglycemia, "borderline" for weak context, "not_relevant" for off-topic
- `bariatric_context`: Should be "strong" if bariatric surgery mentioned directly, "weak" for indirect mentions, "none" if absent
- ❌ Flag if: Clearly PBH-related but marked "not_relevant" or vice versa

**Audience (Who wrote this?):**
- `audience_label`: Should match the post author - patient, HCP, caregiver, researcher, mixed
- ❌ Flag if: Patient story marked as "HCP" or caregiver marked as "patient"

**Sentiment & Emotions:**
- `sentiment_label`: Should match post tone - positive, negative, neutral, mixed
- `emotions`: Array of emotions present - frustration, hope, anxiety, relief, etc.
- ❌ Flag if: Clearly frustrated post marked "positive" or emotions don't match content

**Intent:**
- `intent`: What the author is trying to do - seeking_info, sharing_experience, asking_advice, providing_support, etc.
- ❌ Flag if: Question post has no "seeking_info" intent

**Entity Extraction:**
- `symptoms`: Should capture symptoms mentioned - dizziness, nausea, shakiness, etc.
- `treatments`: Should capture treatments discussed - avexitide, dietary changes, CGM, etc.
- `conditions`: Should capture medical conditions - PBH, diabetes, GERD, etc.
- `companies`: Should capture company mentions - Amylyx, Novo Nordisk, etc.
- `topics`: Should capture discussion topics - bariatric_surgery, access_coverage, diagnostics_monitoring, dietary_modification
- ❌ Flag if: Post mentions "dizzy" but symptoms field is empty, or mentions "Amylyx" but companies field is empty

**Themes:**
- `themes`: High-level categories derived from content - Symptoms, Treatments, Bariatric Surgery, Access & Coverage, Diagnostics, Diet
- ❌ Flag if: Theme doesn't align with the post content

**Flags (Critical for Safety!):**
- `flags`: Special alerts - adverse_event, crisis, misattribution, clinical_trial
- ❌ Flag if: Missing "adverse_event" when patient reports side effects from avexitide, or missing "crisis" for self-harm language

**Key Phrases:**
- `key_phrases`: Important quotes or phrases from the post
- ❌ Flag if: Doesn't capture the most important parts of the post

**Engagement:**
- `engagement_label`: Post impact - high, medium, low (based on likes/comments/shares)
- ❌ Flag if: Calculation seems wrong for the metrics provided

#### 2. How to Document Issues

**Use phase2_review_template.csv:**

**Summary Section (fill out once):**
- Date of review
- Your name
- Number of samples reviewed
- Number of issues found
- Status: "Approved" or "Needs_Iteration"
- Overall notes: Brief summary of patterns

**Issue Log (one row per problem):**
- `Sample_ID`: Post identifier from CSV (source_id)
- `Field_Name`: Which enrichment field is wrong (e.g., "relevance_label", "emotions", "flags")
- `Issue_Description`: What's wrong in plain English
- `Expected_Value`: What it should be
- `Actual_Value`: What the system returned
- `Severity`:
  - **critical** = Blocks production (e.g., missed adverse event)
  - **major** = Needs fix before launch (e.g., wrong relevance on clear cases)
  - **minor** = Nice to fix but not blocking (e.g., minor sentiment mismatch)
- `Notes`: Any additional context

#### 3. How to Share with Dev Team

**Email or Teams message with:**
1. Completed `phase2_review_template.csv` attached
2. Brief summary: "Found 3 issues across 25 samples (92% accurate). Need iteration on relevance scoring."
3. Highlight critical issues if any: "Critical: 1 missed adverse event flag"

### Dev Team: How to Diagnose and Respond

#### When You Receive TCD Feedback:

**Step 1: Review the Issue Log**
- Open `phase2_review_template.csv`
- Focus on **critical** and **major** severity issues first
- Look for patterns (e.g., "all caregiver posts misclassified")

**Step 2: Diagnose Root Cause**
Check these common causes:
- **Dictionary issue**: Term missing from `PBH_SIGNAL_DICTIONARY_v5.txt`
- **Prompt issue**: System prompt needs clearer instructions for this scenario
- **Schema issue**: Response format schema missing or unclear for this field
- **Edge case**: Test data doesn't cover this scenario

**Step 3: Fix and Re-test**

**Note:** Team to determine who is responsible for fixes (may be TCD or Dev team depending on the issue type - e.g., dictionary updates often handled by TCD, code changes by Dev team).

1. Update dictionary/prompt/schema as needed
2. Re-run Phase 1 automated tests (all 44 must still pass)
3. Manually test the problematic samples
4. Document what was fixed

**Step 4: Report Back to TCD**
Email or Teams with:
- "Fixed [X] issues in [component] (dictionary/prompt/schema)"
- Brief explanation of what was changed
- "Re-ran Phase 1: 44/44 passing"
- "Ready for Phase 2 re-review" (if needed) OR "Proceeding to Phase 3" (if approved)

---

## Phase 3: Front-End/Dashboard Testing (TCD + Dev Teams)

**WHO:** TCD team + Dev team collaboration
**WHEN:** After Phase 1 & 2 pass (enrichment validated)
**TIME:** 2-3 hours for comprehensive testing
**GOAL:** Verify dashboard and chatbot work correctly with enriched data

### What to Test

#### Dashboard Features
Test all dashboard modules with real enriched data:
- ✅ **Data visualizations** display correctly (charts, metrics, trends)
- ✅ **Filters work** properly (themes, sources, dates, etc.)
- ✅ **High Impact Posts** show relevant content with correct URLs
- ✅ **Post relevance** matches enrichment output (spot check)

#### Chatbot Testing 🤖

**System Prompt:** *(TBD - in development)*
**Test Scenarios:** *(TBD - will be defined after prompt finalized)*

Verify chatbot functionality:
- ✅ **Query understanding:** Chatbot interprets PBH-related questions correctly
- ✅ **Data accuracy:** Returns correct information from enriched posts
- ✅ **Source citations:** Cites posts/sources appropriately
- ✅ **Edge case handling:** Manages unclear queries, no results, off-topic questions

### Pass Criteria
- ✅ Dashboard displays all data accurately
- ✅ Filters function correctly
- ✅ Chatbot responds appropriately to test queries
- ✅ No critical bugs or data mismatches

### If Issues Found
- 📸 **Document with screenshots** showing the issue
- 📝 **Describe expected vs actual** behavior
- 📧 **Report to dev team** via email/Teams with details


---

## Test Categories (44 Total)

### Adverse Event Tests (12 cases)
**Location:** `../enrichment-test-data-v5/ae-test-cases/`
**Purpose:** Validate FDA-aligned AE detection for avexitide
- 5 should flag `adverse_event`
- 7 should NOT flag

**Critical:** All 5 flagging cases MUST pass.

### Platform Coverage Tests (8 cases)
**Location:** `../enrichment-test-data-v5/platform-coverage/`
**Purpose:** Validate 4-platform MVP support
- 2 Reddit (relevant + borderline)
- 2 TikTok (HCP + patient)
- 2 Facebook (trial + patient story)
- 2 Instagram (influencer + personal)

### Edge Case Tests (8 cases)
**Location:** `../enrichment-test-data-v5/edge-cases/`
**Purpose:** Test robustness
- Weak bariatric context
- No bariatric context (not relevant)
- Multiple companies (SOV accuracy)
- Multiple treatments (dictionary extraction)
- Misspellings/abbreviations
- Very long post (narrative)
- Very short post (minimal data)
- Mixed sentiment (complex emotions)

### Dictionary Tests (6 cases) ✨ NEW
**Location:** `../enrichment-test-data-v5/dictionary-tests/`
**Purpose:** Validate entity extraction robustness
- Negation suppression ("NOT having symptoms")
- Hypothetical context ("MIGHT cause nausea")
- Exclusion rules ("Novo restaurant" ≠ Novo Nordisk)
- Past tense handling ("USED TO have")
- Casual language ("sugar crashes", "wonky")
- Context-dependent words ("sweet" as adjective vs symptom)

### Classification Tests (6 cases) ✨ NEW
**Location:** `../enrichment-test-data-v5/classification-tests/`
**Purpose:** Validate audience/sentiment nuance
- Mixed role (HCP with personal PBH experience)
- Caregiver perspective (spouse describing symptoms)
- Researcher content (academic study)
- Off-topic (bariatric forum but no PBH)
- Sarcasm detection ("Love getting dizzy")
- Clinical neutral tone (medical documentation)

### Flag Tests (4 cases) ✨ NEW
**Location:** `../enrichment-test-data-v5/flag-tests/`
**Purpose:** Validate crisis and misattribution flags
- Crisis language (self-harm ideation)
- Borderline crisis (despair with hope)
- Multiple flags (AE + misattribution)
- False positive crisis (dark humor)

**Critical:** Crisis detection MUST work correctly (patient safety).

---

## Reporting Results to TCD Team

### Required Information
After each test run, report the following via **email or Teams**:

**Test Run Summary:**
- **Date:** YYYY-MM-DD
- **Overall Pass Rate:** X% (e.g., 43/44 tests = 97.7%)
- **Field Accuracy:** X% (from comparison summary)
- **Model:** gpt-4o-2024-08-06
- **Test Count:** 44 (or subset if partial run)

**If Failed Tests:**
- **Failed Test Names:** List specific tests that failed
- **Failure Patterns:** Systematic issues (e.g., "all dictionary exclusion tests failing")
- **Example Failures:** Copy 1-2 specific field mismatches from output

**Attachments (if helpful):**
- Failed test actual outputs (from `../enrichment-test-data-v5/actual_outputs/`)
- Full terminal output (copy/paste or screenshot)

---

## Next Steps After Testing

### If Pass Rate ≥98% ✅
**Phase 1 Complete!** Automated test suite validated.

**Report to TCD Team:**
- Email/Teams with test summary (see above)
- "v5 automated suite: 97.8% pass rate, 99.0% field accuracy - PASSED"

**Next: Phase 2 - Real Sample Data**
1. **TCD team will request real production samples**
   - Normalized JSON format (matching test data structure)
   - Diverse content types from real platforms

2. **Where to send samples:**
   - Email directly to TCD team, OR
   - Share via Teams channel

3. **TCD will validate** enrichment quality on real-world data

4. **Iteration** if needed based on real data findings

### If Pass Rate <95% ⚠️
**Phase 1 Needs Review**

**Report to TCD Team:**
- Email/Teams with detailed failure information
- Include specific test failures and patterns
- Attach failed test actual outputs

**TCD Team Will:**
1. Review failures
2. Update v5 system files (dictionary, prompt, schema)
3. Provide updated files for re-testing

**Your Next Steps:**
1. Wait for updated v5 files from TCD
2. Replace system files in package
3. Re-run tests
4. Report new results

---

**Last Updated:** 2025-11-21
**Version:** v5.0
**Test Count:** 44 cases across 6 categories (4-platform MVP)
