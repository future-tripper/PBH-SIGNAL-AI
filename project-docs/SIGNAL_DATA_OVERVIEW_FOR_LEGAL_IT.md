# SIGNAL Platform: Data Collection & Storage Overview

**For: Amylyx IT & Legal Teams**

---

## Data Sources

**Platform Coverage:**
- Reddit (via Reddit API)
- Facebook, Instagram, TikTok (via YouScan API)

**Collection Scope:**
- Public posts only - no private accounts, closed groups, or restricted content
- Standard API access in compliance with platform Terms of Service
- YouScan handles platform ToS compliance for Facebook/Instagram/TikTok data

---

## What We Store

Based on publicly available information from social media posts:

**Content:**
- Post text and captions
- Post titles (where applicable)
- Source URL and platform identifier

**Author Information (as publicly displayed):**
- Display name/handle
- Author ID (platform-generated identifier)
- Publicly visible profile data (follower counts, demographics when available)

**Engagement Metrics:**
- Likes, comments, shares (public counts)

**Metadata:**
- Publication date/time
- Language
- Geographic indicators (when publicly available)
- Platform and subsource (e.g., subreddit, page)

**Our Analysis:**
- Sentiment classification
- Entity extraction (conditions, treatments, topics)
- Theme categorization

---

## What We Do NOT Store

- Email addresses or phone numbers
- Private messages or direct communications
- Medical records or clinical data
- Payment information
- Content from private/protected accounts
- Personal contact information beyond public display names

---

## Data Storage & Use

- Stored in secure database (Algolia) for dashboard and insights access
- Used exclusively for market insights and patient voice analysis
- No patient identification, recruitment, or direct outreach
- Platform access provided as a service - client does not retain underlying data

---

**Questions?** Contact The Considered team for additional information.
