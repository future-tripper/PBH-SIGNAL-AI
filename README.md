# SIGNAL: Social Listening Platform

AI-powered social listening platform for Amylyx Pharmaceuticals to support the launch of Avexitide, a treatment for Post-Bariatric Hypoglycemia (PBH).

## What It Does

SIGNAL processes social media posts, forum discussions, and healthcare content to extract insights about:
- Patient experiences and sentiment
- Healthcare provider perspectives
- Treatment discussions and adverse events
- Bariatric surgery context and PBH symptoms

## Platform Coverage

Current MVP supports 4 platforms:
- Reddit
- TikTok
- Facebook
- Instagram

## Data Pipeline

1. **Fetching** - Collect data from social sources
2. **Normalizing** - Standardize to common schema
3. **Enriching** - AI-powered entity extraction and classification
4. **Storing** - Database with filtering for dashboard and chatbot

## Project Structure

```
PBH-SIGNAL-AI/
├── CLAUDE.md                    # AI assistant guidance for this project
├── project_docs/                # Documentation and tracking
├── reference_schemas/           # Schema definitions and feature specs
├── enrichment_system/           # Versioned enrichment systems
│   └── v5/                      # Current production system
└── system/v5/                   # Testing infrastructure
```

## Key Features

- **Dictionary-based entity extraction** - Symptoms, treatments, conditions, companies, topics
- **Audience detection** - Patient, HCP, caregiver, researcher perspectives
- **Sentiment analysis** - Positive, negative, neutral, mixed sentiment with emotions
- **Adverse event flagging** - FDA-aligned detection for patient safety
- **Crisis detection** - Self-harm language and misattribution flags
- **Relevance scoring** - Bariatric context triangulation for filtering

## Current Focus

Production testing of enrichment accuracy across multiple platforms with comprehensive test coverage including adverse event detection, platform-specific content handling, and edge case validation.

---

**Last Updated:** 2025-11-21
