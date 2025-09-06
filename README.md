# SIGNAL Enrichment System

Social listening platform for Amylyx PBH treatment launch with AI-powered entity extraction and classification.

## Project Structure

```
SIGNAL/
├── README.md                                    # This file
├── project_docs/                               # Project documentation
│   ├── CLAUDE.md                              # Claude Code guidance
│   └── ENRICHMENT_TEST_TRACKER.md             # Test tracking and issues
├── reference_schemas/                          # Reference CSV files (read-only)
│   ├── PBH_SIGNAL_DICTIONARY.csv             # Dictionary in CSV format
│   ├── PBH_SIGNAL_ENRICHMENT_SCHEMA.csv      # Enrichment schema reference
│   ├── PBH_SIGNAL_NORMALIZATION_SCHEMA.csv   # Input normalization schema
│   └── PBH_SIGNAL_DASHBOARD_FEATURES.csv     # Dashboard requirements
├── test_data/                                 # Test cases for validation
│   ├── reddit_example_1.json                 # Patient voice, relevant, negative
│   ├── reddit_example_2.json                 # HCP voice, relevant, positive
│   ├── reddit_example_3.json                 # Borderline relevance, neutral
│   └── reddit_example_4.json                 # Not relevant (T1D control)
├── enrichment_system/                        # Active development files
│   └── v1/                                   # Version 1 (current baseline)
│       ├── PBH_SIGNAL_DICTIONARY_v1.txt      # Optimized dictionary
│       ├── openai_assistant_system_prompt_v1.md # Optimized system prompt
│       └── openai_assistant_response_format_v1.json # JSON schema
└── [Active Files - Working Versions]
    ├── PBH_SIGNAL_DICTIONARY.txt             # Current dictionary (editable)
    ├── openai_assistant_system_prompt.md     # Current prompt (editable)  
    └── openai_assistant_response_format.json # Current schema (editable)
```

## Development Workflow

### Current Phase: Testing & Optimization
1. **Active Files**: Edit `PBH_SIGNAL_DICTIONARY.txt`, `openai_assistant_system_prompt.md`, `openai_assistant_response_format.json` in root
2. **Testing**: Use files from `test_data/` to validate enrichment accuracy
3. **Tracking**: Document results in `project_docs/ENRICHMENT_TEST_TRACKER.md`
4. **Versioning**: When significant improvements are made, copy to `enrichment_system/vX/` with version suffix

### Version Control Strategy
- **Root files**: Current working versions (editable)
- **enrichment_system/vX/**: Stable versions with timestamp and changelog
- **reference_schemas/**: Static CSV references (don't edit)
- **test_data/**: Test cases (add new ones as needed)

## Next Steps
1. Test v1 enrichment system with Reddit examples
2. Identify and fix issues iteratively  
3. Create v2 when major improvements are achieved
4. Repeat until >90% test accuracy achieved

*Created: September 4, 2024*