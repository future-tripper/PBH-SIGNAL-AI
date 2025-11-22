# Phase 1 Testing: Comparison & Diagnosis Guide

## Your Role

You're helping the dev team compare test outputs, diagnose issues, and recommend fixes for the v5 enrichment system.

**Before starting, review:**
- **CLAUDE.md** (project root) - Full v5 system context, business rules, testing protocol
- **phase1_test_results.csv** - Tracking structure and component definitions (detailed instructions in header)

**Your tasks:**
1. Compare actual outputs vs expected outputs (field-by-field)
2. Populate CSV with results, issues, and fix recommendations
3. Identify failure patterns (systematic vs. random)
4. Generate summary report with priority fixes

**Files:**
- Actual outputs: `actual_outputs/` (44 JSON files from dev team's enrichment run)
- Expected outputs: `../enrichment-test-data-v5/expected-outputs/` (organized by category subdirectories)
- Tracking: `phase1_test_results.csv` (one row per test case)

---

## How to Diagnose Issues

When tests fail, diagnose the root cause to recommend the right fix:

### **Dictionary Issues**
**File:** `../enrichment/PBH_SIGNAL_DICTIONARY_v5.txt`

**Symptoms:**
- Missing entity extractions (e.g., no symptoms captured when post clearly mentions them)
- Wrong entities captured (e.g., extracted "Novo restaurant" as company "Novo_Nordisk")
- Inconsistent extractions (e.g., sometimes captures "shakiness", sometimes misses it)

**Root causes to check:**
- **Missing terms:** Entity not in dictionary at all
- **Missing variations:** Term in dictionary but common variations not listed (e.g., "shaky" variation missing)
- **Exclusion rules too broad:** Exclude terms blocking valid extractions (e.g., "novo restaurant" excluding all "novo")
- **Wrong category:** Term in wrong dictionary category (e.g., symptom listed under conditions)

**Example fix:**
```
"Missing 'shakiness' in symptoms array - post says 'feeling shaky after meals'"
→ Recommended Fix: "Add shakiness variations to PBH_SIGNAL_DICTIONARY_v5.txt:
   Category: symptoms, Label: shakiness, Variations: shaky|trembling|tremors|jittery|shaking hands"
```

---

### **Prompt Issues**
**File:** `../enrichment/openai_assistant_system_prompt_v5.md`

**Symptoms:**
- Wrong classifications (e.g., patient marked as HCP, positive sentiment marked as negative)
- Missing flags (e.g., clear adverse event not flagged, crisis language not detected)
- Incorrect calculated fields (e.g., relevance_label wrong, bariatric_context misclassified)
- Logic not followed (e.g., weak context + 2 symptoms should be borderline but marked not_relevant)

**Root causes to check:**
- **Unclear criteria:** Classification logic ambiguous or not specific enough
- **Missing edge cases:** Instructions don't cover this scenario (e.g., caregiver perspective, sarcasm)
- **Conflicting rules:** Multiple instructions that contradict each other
- **Insufficient emphasis:** Critical rules not highlighted (e.g., "MUST" vs. "should")

**Example fix:**
```
"Missing adverse_event flag - post says 'after starting avexitide I got dizzy'"
→ Recommended Fix: "Update adverse_event criteria in openai_assistant_system_prompt_v5.md (lines 230-273):
   Add stronger emphasis on temporal causal language: 'after starting', 'since going on', 'ever since'
   Add example: 'Been taking avexitide for 2 weeks and having terrible headaches since I started'"
```

---

### **Schema Issues**
**File:** `../enrichment/openai_assistant_response_format_v5.json`

**Symptoms:**
- Fields consistently empty when they should have values
- Arrays too short (e.g., only 1 symptom captured when multiple present)
- Data type mismatches (e.g., string where array expected)
- Constraint violations (e.g., confidence scores outside 0-1 range)

**Root causes to check:**
- **minItems too high:** Array requires minimum items but can't always meet it (e.g., emotions minItems: 2)
- **maxItems too low:** Array can't capture all relevant items (e.g., symptoms maxItems: 3 but 5 present)
- **Enum missing values:** Field can only be specific values but valid option missing
- **Required field shouldn't be:** Field marked required but sometimes legitimately null

**Example fix:**
```
"emotions array always empty even when clear emotions present"
→ Recommended Fix: "Update openai_assistant_response_format_v5.json:
   Change emotions minItems from 1 to 0 (allow empty array when no clear emotions)"
```

---

## Common Failure Patterns

**Pattern 1: All AE tests failing**
→ **Root cause:** AE criteria in prompt not working correctly
→ **Look at:** adverse_event section in system prompt (lines 230-273)
→ **Common issues:** Causal language not detected, Amylyx trial context not recognized, hearsay not excluded

**Pattern 2: All tests in one category missing specific entity type**
→ **Root cause:** Dictionary missing terms for that entity type
→ **Look at:** PBH_SIGNAL_DICTIONARY_v5.txt for that category
→ **Common issues:** Missing drug names, missing symptom variations, wrong category placement

**Pattern 3: All sentiment mismatches on mixed/borderline cases**
→ **Root cause:** Sentiment classification logic needs PBH-specific adjustments
→ **Look at:** sentiment_label section in system prompt
→ **Common issues:** Not accounting for "symptom + hope" = mixed, sarcasm detection

**Pattern 4: Relevance_label consistently wrong on weak context cases**
→ **Root cause:** Relevance triangulation logic not handling edge cases
→ **Look at:** relevance_label section in system prompt (lines 97-116)
→ **Common issues:** Weak context + 2 symptoms should be borderline, not not_relevant

**Pattern 5: Random scattered failures across different fields**
→ **Root cause:** Model variability, not systematic issue
→ **Action:** Acceptable if <5% of tests, no fix needed

---

## Tolerance Rules

### **Zero Tolerance (Must Match Exactly):**
- **adverse_event flag:** False positive or false negative = FAIL (FDA compliance)
- **crisis flag:** False positive or false negative = FAIL (patient safety)
- **relevance_label:** Wrong classification = FAIL (critical for filtering)

### **Acceptable Variation:**
- **Dictionary extraction:** Captured 4/5 symptoms = PASS if major entities present
- **Confidence scores:** ±0.1-0.2 tolerance (e.g., 0.85 vs. 0.90 acceptable)
- **Emotions:** Don't need exact match, but major emotions must align (anxiety + fear vs. anxiety + frustration = acceptable)
- **Key phrases:** Don't need exact phrases, but must capture main concepts
- **Sentiment on mixed cases:** Borderline acceptable if tone is genuinely ambiguous

### **Focus on Patterns:**
- **Systematic failures** (all AE tests failing) = critical issue requiring fix
- **Clustered failures** (3/6 dictionary tests failing) = likely root cause pattern
- **Random failures** (<5% scattered) = acceptable model variation, not systematic

---

## Summary Report Format

After comparing all 44 tests, generate this report:

```markdown
# Phase 1 Test Results Summary

## Overall Results
- **Total Tests:** 44
- **Passed:** X/44 (X%)
- **Partial:** X/44
- **Failed:** X/44
- **Field Accuracy:** X% (matching fields / total fields compared)

## Pass Rate by Category
- AE Test Cases: X/12
- Platform Coverage: X/8
- Edge Cases: X/8
- Dictionary Tests: X/6
- Classification Tests: X/6
- Flag Tests: X/4

## Critical Test Status
- ✅/❌ **AE Flagging:** X/12 AE tests passing (MUST be 12/12)
- ✅/❌ **Crisis Detection:** X/4 crisis tests passing (MUST be 4/4)

## Failure Patterns
[Describe clustering if present]
- Example: "All 4 AE failures show missing adverse_event flag on temporal causal language"
- Example: "3 dictionary test failures all missing GLP-1 drug name variations"
- Example: "No pattern - 2 scattered failures across different components"

## Recommended Priority Fixes

**1. [Most Critical - usually AE or crisis]**
- Issue: [What's wrong]
- File: [Which file to update]
- Fix: [Specific change to make]
- Re-test: [Which tests to re-run]

**2. [Second Priority - usually dictionary or relevance]**
- Issue: [What's wrong]
- File: [Which file to update]
- Fix: [Specific change to make]

**3. [Third Priority - usually sentiment or classification]**
- Issue: [What's wrong]
- File: [Which file to update]
- Fix: [Specific change to make]

## Assessment
- ✅ **PASS - Ready for Phase 2** (≥95% pass rate, ≥98% field accuracy, all critical tests pass)
- ⚠️ **NEEDS ITERATION** (Fix issues above and re-test)
```

---

## Success Criteria

**Phase 1 passes when:**
- ✅ Pass rate ≥95% (42+/44 tests)
- ✅ Field accuracy ≥98%
- ✅ All AE flagging tests passing (12/12)
- ✅ All crisis detection tests passing (4/4)

**If not passing:** Implement recommended fixes, re-run tests, repeat until criteria met.

---

## Quick Reference

**CSV Columns:**
- Date, Version, Tester, Test_Case, Category, Pass_Fail
- Component results: Dictionary_Extraction, Relevance_Logic, Sentiment_Analysis, Audience_Detection, AE_Flagging, Crisis_Detection
- Key_Issues, Recommended_Fixes, Next_Actions, Notes
- See CSV header for detailed component definitions

**v5 System Files:**
- Dictionary: `../enrichment/PBH_SIGNAL_DICTIONARY_v5.txt`
- System Prompt: `../enrichment/openai_assistant_system_prompt_v5.md`
- Response Schema: `../enrichment/openai_assistant_response_format_v5.json`

**For more context:**
- Full v5 system details: CLAUDE.md (project root)
- Testing workflow: TESTING_GUIDE.md
- Expected outputs: `../enrichment-test-data-v5/expected-outputs/` (organized by category)
