# v4 Archive - November 2025

**Archived:** November 20, 2025
**Reason:** v5 released with enhanced avexitide-specific adverse event detection

---

## v4 System Files

This archive contains the production v4 enrichment system files that were in use before v5 enhancement:

1. **PBH_SIGNAL_DICTIONARY_v4.txt** - Entity extraction dictionary (51 entries)
2. **normalization_schema_v4.json** - Input data structure (20 fields)
3. **openai_assistant_response_format_v4.json** - Output schema (42 fields)
4. **openai_assistant_system_prompt_v4.md** - AI instructions for enrichment

---

## v4 Capabilities

- **Platforms:** 5-platform MVP (Reddit, TikTok, Facebook, Instagram, Twitter*)
- **Accuracy:** 98.05% on v3 test cases (19/19 passing)
- **Test Cases:** 14 production examples across all platforms
- **AE Detection:** Basic `adverse_event` flag for any treatment with simple criteria

---

## v4 Adverse Event Detection (Pre-v5)

**Simple Rule:**
- Patient explicitly states treatment CAUSED symptoms
- NOT for treatment suggestions or recommendations

**Example:**
```
"After starting acarbose I became dizzy and nauseous."
→ flags: ["adverse_event"]
```

**Limitations:**
- Flagged ALL treatments (not avexitide-specific)
- No third-person support
- No FDA-aligned criteria
- No hearsay/hypothetical exclusions

---

## What Changed in v5

### Enhanced AE Detection (Avexitide-Only)
- FDA-aligned 3-criteria rule (product + causality + symptoms)
- Third-person reporting support ("My aunt...", "A patient...")
- Explicit exclusions (hearsay, hypotheticals, suggestions, other drugs)
- Symptom suppression in non-actual contexts

### Files Modified
- **System Prompt:** ~45 lines updated (AE criteria + examples + suppression rules)
- **Other Files:** No changes (schema, dictionary unchanged)

---

## Restoration Instructions

If you need to revert to v4:

1. Copy files from this archive back to `/enrichment_system/v4/`
2. Update reference schemas to v4 versions
3. Remove v5-specific features from dashboard (AE Reporting module)

---

## Test Results (v4)

**v3 Regression Test:** 19/19 passing (98.05% accuracy)
- 11 Reddit cases
- 8 TikTok cases

**v4 Platform Test:** 14 production examples
- 3 Reddit
- 3 TikTok
- 3 Facebook
- 3 Instagram
- 2 Twitter (note: text content unavailable)

---

## Related Documentation

- See `enrichment_system/v5/AE_DETECTION_RULES_v5.md` for v5 changes
- See `project_docs/ENRICHMENT_TEST_RESULTS.csv` for historical test results
- See `CLAUDE.md` in project root for overall system architecture

---

**Archived by:** Claude Code
**Version Control:** This is a stable snapshot of v4 for reference and potential rollback
