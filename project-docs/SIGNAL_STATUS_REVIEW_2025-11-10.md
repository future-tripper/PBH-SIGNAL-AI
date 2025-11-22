# SIGNAL Platform - Status Review
**Meeting Brief | November 10, 2025**

---

## 1. DATA PIPELINE ISSUES

**Only Reddit Posts Appearing**
- Frontend shows filters for all sources but only Reddit data visible in posts
- **Action Required:**
  - Verify YouScan API is returning Instagram, Facebook, TikTok data
  - Query Supabase: `SELECT source, COUNT(*) FROM posts GROUP BY source;`
  - Check if non-Reddit posts exist but aren't displaying in frontend
- Note: Platform coverage confirmed as Reddit, Instagram, Facebook, TikTok (appropriate scope)

**Twitter Platform - Remove from Workflow**
- Twitter posts have no text content due to API restrictions
- Cannot enrich without text content
- **Action:** Exclude Twitter source filter from workflow entirely

---

## 2. DATA QUALITY & FILTERING

**Verify v4 Enrichment Implementation**
- **Action Required:** Confirm enrichment is using v4 system prompt rules for:
  - **PBH Relevance:** Triangulation logic (bariatric_context + symptoms + conditions + treatments)
  - **Audience Classification:** Patient vs HCP detection using dictionary anchor patterns
  - **Engagement Scoring:** Formula = likes + (2 × comments) + (3 × shares)
- **Verify Database Schema:** Check these v4 enrichment fields exist in Supabase and are being populated:
  - `engagement_score` (integer), `engagement_label` ("low"/"med"/"high")
  - `audience_label` ("patient"/"hcp"/"industry"/"media"/"unknown"), `audience_confidence` (0.0-1.0)
  - `relevance_label` ("relevant"/"borderline"/"not_relevant"), `relevance_confidence` (0.0-1.0)
- **Impact if missing:** Dashboard features will break (High Impact Posts, audience filters, relevance filters)
- Query: `SELECT column_name FROM information_schema.columns WHERE table_name = 'posts';`

**No Relevance Filter in Workflow**
- Current flow: Fetch → Normalize → Store (all posts) → Enrich → Update
- Posts marked `relevance_label: "not_relevant"` remain in database
- **Recommendation:** Enrich BEFORE storing, drop posts marked "not_relevant"
- **Alternative:** Add filter to dashboard queries `WHERE relevance_label IN ('relevant', 'borderline')`

**Dictionary & Prompt Review Required**
- **System prompt reference:** Currently says "using PBH SIGNAL DICTIONARY (File Search)" but dictionary is embedded in prompt
- **Action:** Update prompt to remove File Search reference, OR consider making dictionary a separate tool if performance issues arise
- **Critical Review Needed - Dictionary Structure:**
  - **Categories:** Enrichment output fields (audience_anchor, symptoms, conditions, treatments, companies, topics)
  - **Labels:** Exact terms to extract and store (e.g., "PBH", "shakiness", "avexitide")
  - **Variations:** Pattern examples to help AI recognize when to extract the Label (NOT exhaustive)
  - **All present variations should tag with the LABEL for storage**
- **Dashboard Taxonomy Clarification:**
  - **Themes:** Used as dashboard FILTERS (derived from enrichment: "Symptoms" if symptoms.length > 0, "Treatments" if treatments.length > 0, etc.)
  - **Topics:** Tagged in enrichment `topics` field for CHATBOT use, NOT dashboard filters
  - **Action:** Review dictionary and prompt to ensure categories, themes, and topics are correctly distinguished and implemented

---

## 3. DASHBOARD FEATURES

**Top Authors Leaderboard**
- Current "Unique authors" metric should be transformed into a comprehensive leaderboard
- **Requirements:**
  - Rank top authors by total post count
  - Rank top authors by engagement level (using engagement_score)
  - Display author details: handle, subscriber count
  - Show their top posts with clickable links to source
- **Note:** This will likely become a v2 feature - discuss implementation timeline and requirements

**Share of Voice (Pie Chart)**
- **Issue:** Pie chart has too many items (overcrowded visualization)
- **Fix Required:** Each tracked item should be ONE piece of the pie
  - Example: "Avexitide" = 1 slice, "Ozempic" = 1 slice, etc.
  - Current implementation appears to fragment items or show unclear groupings
- **Clarification:** Should only show mentions of COMPANIES or TREATMENTS
  - Toggle already exists between Company view and Treatment view
- **Action:** Reduce number of pie slices by consolidating tracked entities

**Audience by Age**
- Section appears empty - need to test and assess
- **YouScan approximates age data** for Instagram/Facebook/TikTok sources
- **Action:** Test with sample posts to confirm age data is being captured and displayed correctly
- Note: Reddit does not provide age data

---

## 4. CHATBOT

**Not Connected to Database**
- Chatbot appears non-functional
- No Algolia integration found in n8n workflow
- Posts stored in Supabase but not indexed to Algolia
- Action: Implement Algolia indexing step in workflow, verify chatbot connection

---

## 5. DESIGN & UX

**Filter Placement & Organization**
- Current: All filters listed horizontally at very top of page (feels cramped/overwhelming)
- Recommendation: Explore more user-friendly placement options:
  - **Sidebar approach:** Move filters to collapsible left sidebar (common pattern for dashboards)
  - **Filter drawer:** Expandable filter panel that slides out when needed (keeps main view clean)
  - **Grouped filters:** If keeping at top, organize into logical groups (Sources, Date Range, Audience Type, etc.)
  - **Smart defaults:** Pre-select most common filters, allow users to "Add filter" as needed
- Current layout with 10+ filter chips side-by-side creates visual clutter
- Consider progressive disclosure: Show 3-4 primary filters, hide advanced filters behind "More filters" button

**General Filtering Issues**
- Need deeper dive into filtering logic - something seems off about the available options
- Action: Review all filter options, validate they align with enrichment fields and user needs
- Questions to explore:
  - Are filter values pulling from actual data or hard-coded?
  - Do filters match enrichment taxonomy (themes, audience labels, etc.)?
  - Are there redundant or misleading filter options?

---

## PRIORITY ACTIONS

**P0 - Critical**
1. **Investigate why only Reddit posts appear** - Query database, verify YouScan API, check frontend display logic
2. **Verify v4 enrichment fields exist in database** - engagement_score, engagement_label, audience_label, audience_confidence, relevance_label, relevance_confidence
3. **Exclude Twitter from workflow** - Remove from source filters
4. **Implement Algolia indexing for chatbot** - Add indexing step to n8n workflow
5. **Add relevance filtering** - Enrich before storing OR filter dashboard queries

**P1 - High Priority**
1. **Review dictionary and prompt implementation** - Verify categories, themes, topics distinction
2. **Fix Share of Voice pie chart** - Reduce to one slice per tracked entity (too many items currently)
3. **Test YouScan age data** - Verify age approximation is working
4. **Discuss Top Authors Leaderboard** - Implementation timeline and v2 requirements
5. **Review filter options and logic** - Ensure alignment with enrichment taxonomy

**P2 - Medium Priority**
1. **Update system prompt** - Remove File Search reference or implement as separate tool
2. **Redesign filter placement** - Sidebar/drawer approach for better UX
3. **Improve responsive design** - Mobile/tablet optimization

---

## QUESTIONS FOR DEV TEAM

**Data Pipeline:**
1. Can you show live YouScan API response? Are Instagram/Facebook/TikTok posts being fetched?
2. Why aren't non-Reddit posts displaying in dashboard?
3. Run query: `SELECT source, COUNT(*) FROM posts GROUP BY source;` - what are the results?

**Enrichment & Database:**
4. **Do v4 enrichment fields exist in Supabase schema?**
   - engagement_score, engagement_label
   - audience_label, audience_confidence
   - relevance_label, relevance_confidence
5. Can you confirm enrichment is using v4 system prompt rules for relevance, audience, and engagement?
6. Are you seeing the dictionary categories vs themes vs topics distinction in the implementation?

**Dashboard:**
7. What does Share of Voice pie chart currently show? Why so many slices?
8. Is YouScan age data working? Can we see examples of posts with age populated?
9. Where are filter values coming from? Are they pulling from actual enrichment data or hard-coded?

**Chatbot:**
10. Is Algolia integration implemented somewhere we haven't seen?
11. Can you demo chatbot functionality with a test query?

---

**END OF BRIEF**
