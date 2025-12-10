#!/usr/bin/env python3
"""
PBH SIGNAL v6.1 - Regression Test Script for v5 Test Data

Tests v6.1 enrichment (prompt + schema) against 44 v5 simulated test cases.

Usage:
    python run_v5_regression_test.py --all         # Run all 44 tests
    python run_v5_regression_test.py --count 5     # Run first 5 tests
    python run_v5_regression_test.py --test-name ae_test_1_first_person_trial  # Single test
"""

import json
import argparse
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Paths
BASE_DIR = Path(__file__).parent
ENRICHMENT_DIR = BASE_DIR.parent / "enrichment"
V5_DATA_DIR = BASE_DIR / "v5-regression-test-data"
OUTPUT_DIR = BASE_DIR / "api_test_outputs" / "v5_regression_v61"

# Test configuration - v6.1 prompt + v6.1 schema
CONFIG = {
    "prompt": "openai_assistant_system_prompt_v6.1_with_dictionary.md",
    "schema": "openai_assistant_response_format_v6.1.json",
    "description": "v6.1 prompt + v6.1 schema (regression test on v5 data)"
}

# Categories to scan for test inputs
CATEGORIES = [
    "ae-test-cases",
    "classification-tests",
    "dictionary-tests",
    "edge-cases",
    "flag-tests",
    "platform-coverage"
]


def load_system_prompt(prompt_file: str) -> str:
    """Load the system prompt"""
    prompt_path = ENRICHMENT_DIR / prompt_file
    if not prompt_path.exists():
        print(f"❌ Prompt file not found: {prompt_path}")
        sys.exit(1)
    with open(prompt_path, 'r') as f:
        return f.read()


def load_schema(schema_file: str) -> dict:
    """Load the JSON schema for structured outputs"""
    schema_path = ENRICHMENT_DIR / schema_file
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    with open(schema_path, 'r') as f:
        return json.load(f)


def discover_test_inputs() -> list:
    """Discover all test input files from v5 regression data directories"""
    inputs = []

    for category in CATEGORIES:
        category_dir = V5_DATA_DIR / category
        if not category_dir.exists():
            print(f"⚠️  Category directory not found: {category_dir}")
            continue

        for json_file in sorted(category_dir.glob("*.json")):
            with open(json_file, 'r') as f:
                data = json.load(f)
            inputs.append({
                "category": category,
                "test_name": json_file.stem,
                "file_path": json_file,
                "data": data
            })

    return inputs


def load_test_inputs(count: int = None, test_name: str = None, run_all: bool = False) -> list:
    """Load test inputs with optional filtering"""
    all_inputs = discover_test_inputs()

    if test_name:
        filtered = [i for i in all_inputs if i["test_name"] == test_name]
        if not filtered:
            print(f"❌ Test not found: {test_name}")
            print(f"Available tests: {[i['test_name'] for i in all_inputs[:5]]}...")
            sys.exit(1)
        return filtered

    if count and not run_all:
        return all_inputs[:count]

    return all_inputs


def call_openai_with_schema(client: OpenAI, system_prompt: str, normalized_input: dict, schema: dict) -> dict:
    """Call OpenAI with structured output schema"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Process this normalized post and return enriched JSON:\n\n{json.dumps(normalized_input, indent=2)}"}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": schema
        },
        temperature=0.1
    )

    return json.loads(response.choices[0].message.content)


def main():
    parser = argparse.ArgumentParser(description="Run v6.1 regression test against v5 test data")
    parser.add_argument("--count", type=int, help="Number of tests to run")
    parser.add_argument("--all", action="store_true", help="Run all 44 tests")
    parser.add_argument("--test-name", type=str, help="Run specific test by name (e.g., ae_test_1_first_person_trial)")
    args = parser.parse_args()

    # Validate args
    if not args.count and not args.all and not args.test_name:
        print("❌ Must specify --count, --all, or --test-name")
        sys.exit(1)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"❌ OPENAI_API_KEY not found. Checked: {env_path}")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"\n{'='*70}")
    print(f"  V5 REGRESSION TEST: {CONFIG['description']}")
    print(f"{'='*70}")
    print(f"  Prompt: {CONFIG['prompt']}")
    print(f"  Schema: {CONFIG['schema']}")

    # Load prompt and schema
    system_prompt = load_system_prompt(CONFIG['prompt'])
    schema = load_schema(CONFIG['schema'])
    print(f"  Prompt loaded: {len(system_prompt):,} chars")

    # Load inputs
    inputs = load_test_inputs(count=args.count, test_name=args.test_name, run_all=args.all)
    print(f"  Tests to run: {len(inputs)}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Output dir: {OUTPUT_DIR}")

    print(f"\n{'='*70}")
    print(f"Processing...")
    print(f"{'='*70}\n")

    results = {
        "total": len(inputs),
        "success": 0,
        "skipped": 0,
        "errors": 0,
        "by_category": {}
    }

    for i, test_input in enumerate(inputs):
        test_name = test_input["test_name"]
        category = test_input["category"]
        output_file = OUTPUT_DIR / f"{test_name}_enriched.json"

        # Track by category
        if category not in results["by_category"]:
            results["by_category"][category] = {"total": 0, "success": 0, "errors": 0}
        results["by_category"][category]["total"] += 1

        # Skip if already exists
        if output_file.exists():
            print(f"[{i+1}/{len(inputs)}] {test_name} - skipped (exists)")
            results["skipped"] += 1
            results["by_category"][category]["success"] += 1
            continue

        print(f"[{i+1}/{len(inputs)}] [{category}] {test_name}...", end=" ", flush=True)

        try:
            enriched = call_openai_with_schema(client, system_prompt, test_input["data"], schema)

            # Merge input fields with enriched output
            full_output = {**test_input["data"], **enriched}

            with open(output_file, 'w') as f:
                json.dump(full_output, f, indent=2, ensure_ascii=False)

            print("✅")
            results["success"] += 1
            results["by_category"][category]["success"] += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            results["errors"] += 1
            results["by_category"][category]["errors"] += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY: V5 Regression Test - v6.1 prompt + v6.1 schema")
    print(f"{'='*70}")
    print(f"Total:   {results['total']}")
    print(f"Success: {results['success']} ✅")
    print(f"Skipped: {results['skipped']} (already existed)")
    print(f"Errors:  {results['errors']} ❌")

    if results["by_category"]:
        print(f"\nBy Category:")
        for cat, stats in sorted(results["by_category"].items()):
            status = "✅" if stats["errors"] == 0 else "❌"
            print(f"  {cat}: {stats['success']}/{stats['total']} {status}")

    print(f"\nOutputs: {OUTPUT_DIR}")
    print(f"\nNext step: python compare_v5_regression.py")


if __name__ == "__main__":
    main()
