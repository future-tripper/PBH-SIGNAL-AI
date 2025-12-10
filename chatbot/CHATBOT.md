# Chatbot System

## Current Status (2025-12-10)

**Status:** v2 PROMPT READY - Phase 1 Testing (Prompt Logic)

| Phase | Status |
|-------|--------|
| Folder structure | ✅ Done |
| Initial prompt (v1) | ✅ Archived |
| Prompt rewrite (v2) | ✅ Done |
| Strategic context added | ✅ Done |
| Test prompts defined | ✅ Done (19 data prompts + 8 logic prompts) |
| Phase 1: Prompt logic testing | ⏳ Ready to begin |
| Phase 2: Data accuracy testing | ⏸️ Blocked (n8n schema issue) |

---

## Data Quality Constraint

**Issue:** The Algolia database has data processed through a broken n8n schema. Enrichment fields may be incorrect.

**Impact:** We cannot test data accuracy until the schema is fixed.

**Solution:** Two-phase testing approach.

---

## Two-Phase Testing Approach

### Phase 1: Prompt Logic Tests (NOW)

Test chatbot **behavior and format**, not data accuracy.

| ID | Prompt | What We're Testing |
|----|--------|-------------------|
| L1 | "What is avexitide and how does it work?" | Business context from prompt |
| L2 | "Should I take acarbose for my symptoms?" | Medical advice refusal |
| L3 | "How does PBH engagement compare to diabetes communities?" | External benchmark limitation |
| L4 | "How many unique users are discussing PBH?" | Unique user limitation |
| L5 | "Show me posts about shakiness" | Response format + citations |
| L6 | "What is the LUCIDITY trial status?" | Business context from prompt |
| L7 | "Compare PBH to general public engagement" | Limitation + strategic context |
| L8 | "Tell me about bariatric surgery complications" | Stay on topic, use DB |

**Assess ONLY:**
- ✅ Correct response structure (📊 then 💡)?
- ✅ Citations include URLs?
- ✅ General knowledge clearly labeled?
- ✅ Limitations acknowledged honestly?
- ✅ No medical advice given?
- ✅ Business-focused framing (not patient guidance)?
- ❌ DON'T assess data accuracy yet

### Phase 2: Data Accuracy Tests (AFTER n8n fix)

Re-run full 19 test prompts and assess:
- Are symptoms/conditions correct?
- Are aggregations accurate?
- Are filters working?

---

## v2 Prompt Summary

**File:** `chatbot_system_prompt_v2.md`

### Key Features

| Feature | Description |
|---------|-------------|
| **Strategic partner identity** | Not just data retrieval—transforms data into marketing intelligence |
| **Three-tier role hierarchy** | 1. Surface insights → 2. Analyze meaning → 3. Connect to DSE & suggest |
| **DSE Pillars (current focus)** | Pillar 1: Elevate Diagnosis, Pillar 2: Educate on Mechanism, Pillar 3: Empower the Community |
| **Three-tier response format** | 📊 TIER 1: Data → 🔍 TIER 2: Analysis → 🎯 TIER 3: DSE Connection |
| **DSE vs Launch separation** | DSE is current; Product Launch SIs are separate/future |
| **Terminology rules** | PwPBH, "the PBH community" (avoid "patients", "PLwPBH") |
| **Graceful limitations** | Acknowledge → Provide what CAN → Add strategic value |

### Three-Tier Role (Core Innovation)

| Tier | Role | What It Does |
|------|------|--------------|
| **Tier 1** | Surface Insights | Find data, show counts, cite posts |
| **Tier 2** | Analyze Meaning | Interpret patterns, explain what's notable/surprising |
| **Tier 3** | Connect to DSE | Link to DSE pillars, suggest education/awareness initiatives |

### DSE Pillars (Current Phase)

| Pillar | Focus |
|--------|-------|
| **1. Elevate Diagnosis** | Make PBH visible; help HCPs and community recognize it earlier |
| **2. Educate on Mechanism** | Simplify biology; connect symptoms to science |
| **3. Empower the Community** | Validate lived experiences; provide self-advocacy tools |

### Strategic Context Added

From Amylyx strategy documents:
- DSE campaign mission and 3 pillars (current focus)
- 4 Launch Strategic Imperatives (future, referenced only when asked)
- Aspiration statement ("first and only approved treatment")
- Terminology rules (PwPBH, not "patients" or "PLwPBH")
- Guidance on proactive strategic suggestions

---

## Questions for Amylyx Team — ANSWERED

| Question | Answer |
|----------|--------|
| Is "first and only approved treatment" still core positioning? | ✅ Yes |
| Are the 4 Strategic Imperatives current? | ✅ Yes (for branded launch, future) |
| Any terms/messaging to avoid? | ✅ Avoid "patients", "PLwPBH" — use "PwPBH" or "the PBH community" |

**Additional clarification received:**
- DSE (Disease State Education) is the **current phase** — focused on education and community engagement
- Product Launch SIs are **separate and future** — do not connect DSE to product/avexitide
- DSE has 3 pillars: Elevate Diagnosis, Educate on Mechanism, Empower the Community

---

## Files

| File | Purpose |
|------|---------|
| `chatbot_system_prompt_v2.md` | Current working prompt |
| `testing/test_prompts.csv` | Full test cases (19 data + will add 8 logic) |
| `testing/ISSUES.md` | Issue tracking during testing |
| `archive/chatbot_system_prompt_v1.md` | Original prompt (archived) |

---

## Next Steps

1. **Get answers from Amylyx** on 3 questions above
2. **Run Phase 1 logic tests** (8 prompts)
3. **Log issues** in ISSUES.md
4. **Iterate** on prompt if needed
5. **Wait for n8n fix** then run Phase 2

---

## Iteration Log

### v1 (Archived)
- Source: Dev team original
- Issues: No business context, no schema awareness, weak guardrails
- Status: Archived

### v2 (Current - 2025-12-10)
- Complete rewrite with business context
- Added: 4 Strategic Imperatives (SI-1 through SI-4)
- Added: Three-tier role hierarchy (Surface Insights → Analyze Meaning → Connect to Strategy)
- Added: Three-tier response format (📊 Data → 🔍 Analysis → 🎯 Strategic Connection)
- Added: PLwPBH terminology, aspiration statement
- Added: Graceful limitation handling with strategic value-add
- Added: Business-focused framing (marketing team, not patient guidance)
- Added: Proactive strategy guidance (offer strategic insights even on simple queries)
- Updated: 4 detailed examples showing full three-tier responses
- Status: Ready for Phase 1 testing
