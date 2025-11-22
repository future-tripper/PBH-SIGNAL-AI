# PBH SIGNAL v5 Enrichment Testing Package

**AI-assisted testing system for validating v5 enrichment with detailed tracking and diagnosis.**

---

## 📦 Package Contents

### Documentation
- **TESTING_GUIDE.md** - Complete 3-phase testing workflow with step-by-step instructions
- **phase1_claude_prompt.md** - Detailed instructions for Claude Code to compare tests and diagnose issues
- **CLAUDE.md** (project root) - Full v5 system context for AI assistant

### Testing Infrastructure
- **phase1_test_results_template.csv** - Clean template for test tracking (one row per test, includes diagnosis columns)
- **phase2_review_template.csv** - Real sample review tracking for Phase 2
- **actual_outputs/** - Where dev team saves enriched test outputs (created when tests run)
- **automation/** - Python scripts for automated testing (Chat Completions API with embedded dictionary)
- **completed_tests/** - Archive of internal testing results (for reference only)

### Test Data (44 cases total)
**Location:** `../enrichment-test-data-v5/` (parent directory)

Test files organized by category:
- `ae-test-cases/` - 12 AE detection tests
- `platform-coverage/` - 8 platform coverage tests (Reddit, TikTok, Facebook, Instagram)
- `edge-cases/` - 8 edge case tests
- `dictionary-tests/` - 6 entity extraction robustness tests ✨ NEW
- `classification-tests/` - 6 audience/sentiment nuance tests ✨ NEW
- `flag-tests/` - 4 crisis/misattribution flag tests ✨ NEW
- `expected-outputs/` - 44 "gold standard" outputs (organized by category subdirectories)

**Note:** Enrichment system files (dictionary, prompt, schema) are in `../enrichment/` folder

---

## ⚙️ Prerequisites: Configure v5 Enrichment System

**Before running tests, ensure your enrichment pipeline is configured correctly with v5 system files.**

### Required Configuration (n8n or API)

**Model Settings:**
- **Model:** `gpt-4o-2024-08-06`
- **Temperature:** `0.3` (balanced for consistency + nuance)
- **Response Format:** `json_schema` with structured output

**System Files (from `../enrichment/` folder):**

1. **System Prompt:**
   - File: `openai_assistant_system_prompt_v5.md`
   - Where: Set as system message in your API call

2. **Response Format Schema:**
   - File: `openai_assistant_response_format_v5.json`
   - Where: Set as `json_schema` in response_format parameter

3. **Dictionary (File Search Tool):** ⚠️ **CRITICAL**
   - File: `PBH_SIGNAL_DICTIONARY_v5.txt`
   - Where: **Attach as File Search tool** (do NOT embed in prompt)
   - **Important:** The dictionary must be attached as a searchable file tool. The system prompt references "File Search" for dictionary lookups (line 8). Embedding the dictionary in the prompt will not work correctly.

**Verification:**
- System prompt mentions "Dictionary-based entity extraction using PBH SIGNAL DICTIONARY (File Search)" → Confirms File Search tool is required
- Test with one input to ensure all three components are loaded correctly

---

## 🚀 Quick Start (AI-Assisted Approach)

### 1. Run Tests Through Your Pipeline
Feed 44 test inputs (from `../enrichment-test-data-v5/`) through your enrichment system.
Save outputs to `actual_outputs/` folder.

### 2. Use Claude Code for Comparison
Open Claude Code with project context (`CLAUDE.md`).
Follow instructions in `phase1_claude_prompt.md` to:
- Compare actual vs expected outputs
- Populate `phase1_test_results_template.csv` with results (save as `phase1_test_results.csv`)
- Get diagnosis and fix recommendations

### 3. Iterate & Improve
Review Claude's recommendations, implement fixes, re-test.
Most systems converge in 2-3 iterations.

### 4. Report to TCD
Email completed `phase1_test_results.csv` with results and summary.

See **TESTING_GUIDE.md** for detailed success criteria and thresholds.

---

## 📊 Test Categories (44 Total)

### Adverse Event Detection (12 tests)
**Purpose:** Validate FDA-aligned AE flagging for avexitide
- 5 should flag `adverse_event` (first-person, third-person, trial context)
- 7 should NOT flag (hearsay, hypotheticals, other treatments)

### Platform Coverage (8 tests)
**Purpose:** Validate 4-platform MVP support
- Reddit, TikTok, Facebook, Instagram
- Patient and HCP perspectives

### Edge Cases (8 tests)
**Purpose:** Test schema robustness
- Weak/no bariatric context
- Multiple companies/treatments
- Misspellings and abbreviations
- Very long/short posts
- Mixed sentiment

### Dictionary Tests (6 tests) ✨ NEW
**Purpose:** Entity extraction edge cases
- Negation suppression, hypothetical context
- Exclusion rules, past tense handling
- Casual language mapping, context-dependent words

### Classification Tests (6 tests) ✨ NEW
**Purpose:** Audience/sentiment nuance
- Mixed roles, caregiver perspective
- Researcher content, off-topic detection
- Sarcasm detection, clinical neutral tone

### Flag Tests (4 tests) ✨ NEW
**Purpose:** Crisis and misattribution flags
- Crisis detection (self-harm language)
- Borderline cases, multiple flags
- False positives (dark humor)

---

## 📖 Full Documentation

See **TESTING_GUIDE.md** for complete testing workflow:
- **Phase 1:** AI-assisted test validation (Dev team + Claude Code)
- **Phase 2:** Real sample data review (TCD team)
- **Phase 3:** Front-end/dashboard testing (TCD + Dev teams)
- Detailed setup, iteration workflow, and reporting guidance

---

## 📝 Reporting Results

After each test run, email or Teams TCD with:

**Test Summary:**
- Date and test count (44 or subset)
- Overall pass rate (e.g., "43/44 = 97.7%")
- Field accuracy (from comparison summary)

**If Tests Failed:**
- List failed test names
- Describe failure patterns
- Attach failed actual outputs if helpful

---

## 🛠️ System Requirements

**For AI-Assisted Testing (Recommended):**
- Enrichment pipeline already set up and working
- Access to Claude Code or similar AI coding assistant
- 30-60 minutes for full Phase 1 (run tests, comparison, iteration)

**For Python Automation (Internal Use):**
- See `automation/` folder for scripts
- Uses Chat Completions API with embedded dictionary (not File Search)
- Requires Python 3.8+, OpenAI API access
- See `completed_tests/` for previous test runs using this approach

---

## 📞 Support

**Questions?** Check TESTING_GUIDE.md first.
**Issues?** Email or Teams TCD team with test results and failures.
**Phase 2?** TCD will reach out for sample data when ready.
**Updates?** Coordinate with TCD team (Joe/Claude) for new gold standards.

---

**Last Updated:** 2025-11-21
**Version:** v5.0
**Total Tests:** 44 cases across 6 categories (4-platform MVP)
**Verified By:** TCD Team (Claude + Joe)
