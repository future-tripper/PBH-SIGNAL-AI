# v3 Chatbot Testing

**Last Updated:** 2025-12-11

---

## Setup Instructions

### Step 1: Update Algolia Tool Description

1. Open Algolia config UI (Configuration tab)
2. Click "Algolia Search" tool → Edit
3. Replace Description with this (exactly 200 chars):

```
PBH social posts (all relevant/borderline). Use facet_filters: symptoms, conditions, treatments, emotions, audience_label, topics, engagement_label, bariatric_context. Example: ["emotions:frustration"]
```

4. Save changes

### Step 2: Update System Prompt

1. Copy full content of `chatbot/chatbot_system_prompt_v3.md`
2. Paste into Instructions box (replace existing)
3. Save changes

### Step 3: Start Fresh Session

1. Start a **new conversation** (not just clear chat)
2. Select model: **5-mini** (or try 4.1)

---

## Test Conversations (C1-C9)

Each test is a **multi-turn conversation**. Run the initial prompt, then each follow-up in sequence.

---

### C1: Side Effects & Symptoms

**Initial:** What side effects and symptoms of bariatric surgery are being discussed?

**Follow-ups:**
1. Which of these are most prominent?
2. What is the sentiment of the posts, is it frustration, determination or are they resigned?
3. What are they looking for, solutions or support?

**What this tests:**
- Symptom filtering
- Pattern identification
- Sentiment analysis
- Context retention

---

### C2: Language/Messaging

**Initial:** Would "spike and crash glucose pattern" or "highs and lows" resonate with the community?

**Follow-ups:**
1. What would be the community alternatives?
2. What about the terms "spike" and "crash", how prominent are they?
3. What are more prominent alternatives for each?
4. And what about spikes, how are they described?
5. Okay, so sugar crash and spike work, but glucose is more often referred to as blood sugar and pattern is very alien

**What this tests:**
- Language analysis in post content
- Term frequency assessment
- Iterative refinement
- Strategic messaging recommendations

---

### C3: HCP Perception

**Initial:** How do PwPBH feel about their doctors or HCPs?

**Follow-ups:**
1. What are the support gaps that need addressing?
2. Of these, which is the most common?
3. Does the community share this insight, such as nutrition guidance, with each other?

**What this tests:**
- Sentiment toward HCPs
- Gap identification
- Community behavior patterns

---

### C4: Popular Content

**Initial:** What is the focus of the most popular posts?

**Follow-ups:**
1. Therefore, what should be the editorial focus of our posts?
2. Anything we should avoid?
3. Share with me a top post and tell me what we can learn in terms of focus, tone, etc.
4. How could this have been improved?

**What this tests:**
- Engagement metrics (engagement_label: high)
- Content analysis
- Strategic recommendations
- Critical evaluation

---

### C5: HCP Discussions

**Initial:** What are HCPs discussing?

**Follow-ups:**
1. Can you see any medical terms, which suggest either HCPs or very informed patients?
2. How does the community react to these more technical discussions?
3. Please identify themes including these more medical narratives?

**What this tests:**
- Audience filtering (audience_label: hcp)
- Technical term identification
- Cross-audience analysis

---

### C6: Language Framing

**Initial:** I'd love to frame "unpredictable hypoglycemic events" in language that the community uses, any thoughts?

**Follow-ups:**
1. Specifically, how does the community describe the unpredictability, I love the "rollercoaster" analogy
2. Do any of these garner agreement or positive sentiment?
3. So, a "rollercoaster of sugar swings" is one way the community might describe "unpredictable hypoglycemic events"

**What this tests:**
- Language translation (clinical → community)
- Metaphor identification
- Sentiment correlation
- Synthesis and confirmation

---

### C7: Influential Voices

**Initial:** Do we have any repeat posters or prominent voices in the communities?

**Follow-ups:**
1. Can I get a table of the more influential voices in each of these categories?
2. For each of these voices, give me a sample / typical post?
3. How does the industry voices compare and how might they improve their impact?
4. Rewrite a post, factoring in these recommendations, showing me before and after?

**What this tests:**
- Author/engagement analysis
- Table formatting
- Cross-category comparison
- Content creation/rewriting

---

### C8: HCP Influencers

**Initial:** In terms of the healthcare voices, who are the most influential?

**Follow-ups:**
1. Please create a table of these influencers including key details / criteria
2. In terms of Stephen Stone, create a detailed profile of all we know of them
3. Give me some content ideas that you think would resonate with Stephen?
4. For each, now create a sample post
5. Which of these would resonate the most and why?

**What this tests:**
- HCP audience filtering
- Influencer profiling
- Persona-based content creation
- Strategic content ranking

---

### C9: Weekly Report

**Initial:** Please produce a report based on your knowledge for the past 7 days

**Follow-ups:**
1. Please provide an executive summary of 3-4 sentences that I can share internally

**What this tests:**
- Time-based filtering (numericFilters on published_at_ts)
- Report generation
- Executive summary synthesis

---

### C10: Time-Based Summaries

**Initial:** Give me a summary of posts from the last month

**Follow-ups:**
1. What are the trending topics compared to previous months?
2. Any notable spikes in activity or sentiment?

**What this tests:**
- Time-based filtering (numericFilters on published_at_ts)
- Trend identification
- Comparative analysis

---

### C11: HCP Voices on Bariatric/PBH

**Initial:** What HCP voices are talking about bariatric surgery or PBH?

**Follow-ups:**
1. What topics are they focusing on?
2. How does their perspective differ from patient voices?

**What this tests:**
- Audience filtering (audience_label: hcp)
- Topic filtering (bariatric_surgery, PBH conditions)
- Cross-audience comparison

---

### C12: Technical/Clinical Terms

**Initial:** Has anyone mentioned CGMs or Whipple's Triad across socials?

**Follow-ups:**
1. Who is using these terms - HCPs or patients?
2. What context are they discussing them in?

**What this tests:**
- Free text search capability (terms not in enum filters)
- Audience identification
- Clinical term recognition

---

## Evaluation Framework

Testing isn't just "did it work?" — we need to understand **WHY** things work or fail:

### Four Dimensions

| Dimension | Who Cares | What We Measure |
|-----------|-----------|-----------------|
| **Functional** | Dev | Filter used? Correct? Data returned? Context retained? |
| **Quality** | Business | Insight useful? Strategic? Citations? |
| **Root Cause** | Both | If it failed, WHY? |
| **Gaps** | Product | What knowledge was missing from prompt? |

### Root Cause Categories

When something fails, identify which bucket:

- `none` — Success
- `prompt_gap` — v3 missing knowledge (e.g., didn't know how to analyze language)
- `functional` — Filter/syntax issue (facet_filters null or wrong)
- `data_limitation` — Info not in database (e.g., author details missing)
- `model_reasoning` — Model failure (e.g., hallucinated despite good data)

**Note on facet_filters:** Previous v2.x testing observed `facet_filters: null` issues, but this was never tested with v1. Watch for filter issues during testing, but don't assume they'll occur—v1/v3 may handle this differently.

---

## CSV Recording

Record results in `v3_test_results.csv` with these columns:

**Identification:**
- `conversation_id`: C1-C9
- `turn_number`: 1, 2, 3... (1 = initial, 2+ = follow-ups)
- `prompt`: The actual prompt text
- `timestamp`: When tested
- `model`: 5-mini, 4.1, etc.

**Functional:**
- `filter_used`: yes / no / null / n/a
- `filter_correct`: yes / partial / no / n/a
- `data_returned`: count (0, 10, 50, etc.)
- `context_retained`: yes / partial / no

**Quality:**
- `insight_quality`: excellent / useful / generic / wrong / hallucinated
- `strategic_relevance`: high / medium / low / none
- `citations`: yes / partial / no
- `hallucination`: none / minor / major

**Root Cause:**
- `failure_root_cause`: none / prompt_gap / functional / data_limitation / model_reasoning
- `prompt_gap_identified`: Free text - what knowledge was needed?
- `notes`: Free text observations

---

## Expected Risk Areas

| Conv | Expected to Work? | Risk Areas |
|------|-------------------|------------|
| C1 | Yes | May give generic insights without community context |
| C2 | Partial | Language analysis methodology not taught |
| C3 | Yes | Should work with audience/emotion filters |
| C4 | Yes | Engagement filters should work |
| C5 | Yes | HCP filter exists |
| C6 | Partial | Clinical→community translation not taught |
| C7 | Risk | Author data may be limited; no guidance on influencer ID |
| C8 | Risk | Same as C7; persona may not exist in data |
| C9 | Yes | Time filters taught |
| C10 | Yes | Time filters taught; trend comparison may be limited |
| C11 | Yes | HCP + topic filters should work |
| C12 | Risk | CGM/Whipple's not in enum filters; relies on free text search |

---

## Test Flow

### During Each Conversation

For each turn:
1. Send prompt
2. **Check tool call** (in Conversations tab):
   - Was facet_filters used?
   - Was it constructed correctly?
   - How many results returned?
3. **Evaluate response**:
   - Did it cite real sources?
   - Was the insight useful or generic?
   - Did it hallucinate?
4. **Record in CSV immediately**

### After Conversation

- Did context carry across turns?
- What went wrong (if anything)?
- What prompt knowledge was missing?

---

## Files

| File | Purpose |
|------|---------|
| `chatbot/chatbot_system_prompt_v3.md` | Current prompt |
| `chatbot/chatbot_system_prompt_v1.md` | Dev's original (reference) |
| `chatbot/testing/v3_test_plan.md` | This file |

---

## Version History

| Version | Prompts | Notes |
|---------|---------|-------|
| v1 | - | Dev's original, untested |
| v2.x | T1-T8 | Single prompts; facet_filters:null issue observed here |
| **v3** | **C1-C12** | v1 + slim business context |
