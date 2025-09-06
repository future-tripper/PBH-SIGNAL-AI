# Test Tracker Usage Guide

## Quick Testing Workflow

### 1. Use the CSV: `ENRICHMENT_TEST_RESULTS.csv`
Simple spreadsheet format - just add a new row for each test run.

### 2. Required Fields:
- **Date**: Test date (YYYY-MM-DD)
- **Tester**: Your name/initials
- **Version**: System version (v1, v2, etc.)
- **Model**: AI model used (e.g., gpt-4o, gpt-4-turbo)
- **Temperature**: Temperature setting (e.g., 0.1, 0.7)
- **Top_P**: Top-p setting (leave blank if not used)
- **Test_Case**: reddit_example_1, reddit_example_2, reddit_example_3, reddit_example_4
- **Pass_Fail**: PASS, FAIL, PARTIAL
- **Key_Issues**: Brief description of main problems found
- **Next_Actions**: What needs to be fixed

### 3. Optional Validation Fields:
Rate each area as: PASS, FAIL, PARTIAL, Not_Tested
- **Dictionary_Extraction**: Are correct Labels being extracted?
- **Relevance_Logic**: Is bariatric_context and relevance_label correct?
- **Sentiment_Analysis**: Is sentiment appropriate for the content?
- **Audience_Detection**: Patient vs HCP detection working?

### 4. Quick Test Process:
1. **Copy test case JSON** from `test_data/`
2. **Paste into OpenAI Assistant** 
3. **Review output** against expected results
4. **Add row to CSV** with results
5. **Note issues** in Key_Issues column
6. **Plan fixes** in Next_Actions column

## Example Entry:
```
2024-09-04,Joe,v1,gpt-4o,0.1,,reddit_example_1,FAIL,FAIL,PASS,PARTIAL,PASS,"Missing shakiness symptom, wrong audience confidence","Fix symptom extraction in dictionary"
```

## Benefits:
- ✅ **Quick to fill out** - just one row per test
- ✅ **Track trends** over time and versions  
- ✅ **Easy to analyze** - import into Excel/Sheets
- ✅ **Focused** on key validation areas
- ✅ **Actionable** - clear next steps

## When to Create New Version:
When you've made significant improvements and want to test them, copy current files to `enrichment_system/v2/` and start testing v2.