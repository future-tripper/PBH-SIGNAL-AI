#!/usr/bin/env python3
"""
PBH SIGNAL v6 - API Test Script for 3 Configurations

Tests enrichment by calling OpenAI API with different prompt/schema combinations:
- Test 1: v6 prompt + v6 schema
- Test 2: v6.1 prompt + v6 schema
- Test 3: v6.1 prompt + v6.1 schema

Usage:
    python run_api_test.py --test 1 --all    # v6 prompt + v6 schema
    python run_api_test.py --test 2 --all    # v6.1 prompt + v6 schema
    python run_api_test.py --test 3 --all    # v6.1 prompt + v6.1 schema
    python run_api_test.py --test 1 --source-id t3_1pcy7kt  # Test specific post
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
NORMALIZED_DIR = BASE_DIR / "normalized_inputs"
OUTPUT_DIR = BASE_DIR / "api_test_outputs"

# Test configurations
TEST_CONFIGS = {
    1: {
        "name": "test1_v6prompt_v6schema",
        "prompt": "openai_assistant_system_prompt_v6_with_dictionary.md",
        "schema": "openai_assistant_response_format_v6.json",
        "description": "v6 prompt + v6 schema"
    },
    2: {
        "name": "test2_v61prompt_v6schema",
        "prompt": "openai_assistant_system_prompt_v6.1_with_dictionary.md",
        "schema": "openai_assistant_response_format_v6.json",
        "description": "v6.1 prompt + v6 schema"
    },
    3: {
        "name": "test3_v61prompt_v61schema",
        "prompt": "openai_assistant_system_prompt_v6.1_with_dictionary.md",
        "schema": "openai_assistant_response_format_v6.1.json",
        "description": "v6.1 prompt + v6.1 schema"
    }
}


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


def load_normalized_inputs(count: int = None, source_id: str = None, run_all: bool = False) -> list:
    """Load normalized input files"""
    if source_id:
        file_path = NORMALIZED_DIR / f"{source_id}.json"
        if not file_path.exists():
            print(f"❌ Input file not found: {file_path}")
            sys.exit(1)
        with open(file_path, 'r') as f:
            return [json.load(f)]

    files = sorted(NORMALIZED_DIR.glob("*.json"))
    if count and not run_all:
        files = files[:count]

    inputs = []
    for f in files:
        with open(f, 'r') as fp:
            inputs.append(json.load(fp))

    return inputs


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
    parser = argparse.ArgumentParser(description="Test v6 enrichment with different prompt/schema configurations")
    parser.add_argument("--test", type=int, choices=[1, 2, 3], required=True,
                        help="Test configuration: 1=v6+v6, 2=v6.1+v6, 3=v6.1+v6.1")
    parser.add_argument("--count", type=int, help="Number of posts to test")
    parser.add_argument("--all", action="store_true", help="Test all posts")
    parser.add_argument("--source-id", type=str, help="Test specific source_id")
    args = parser.parse_args()

    # Validate args
    if not args.count and not args.all and not args.source_id:
        print("❌ Must specify --count, --all, or --source-id")
        sys.exit(1)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"❌ OPENAI_API_KEY not found. Checked: {env_path}")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Get test config
    config = TEST_CONFIGS[args.test]

    print(f"\n{'='*70}")
    print(f"  TEST {args.test}: {config['description']}")
    print(f"{'='*70}")
    print(f"  Prompt: {config['prompt']}")
    print(f"  Schema: {config['schema']}")

    # Load prompt and schema
    system_prompt = load_system_prompt(config['prompt'])
    schema = load_schema(config['schema'])
    print(f"  Prompt loaded: {len(system_prompt):,} chars")

    # Load inputs
    inputs = load_normalized_inputs(count=args.count, source_id=args.source_id, run_all=args.all)
    print(f"  Posts to process: {len(inputs)}")

    # Create output directory
    mode_output_dir = OUTPUT_DIR / config['name']
    mode_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Output dir: {mode_output_dir}")

    print(f"\n{'='*70}")
    print(f"Processing...")
    print(f"{'='*70}\n")

    results = {
        "total": len(inputs),
        "success": 0,
        "errors": 0
    }

    for i, normalized_input in enumerate(inputs):
        source_id = normalized_input.get("source_id", f"unknown_{i}")
        output_file = mode_output_dir / f"{source_id}_enriched.json"

        # Skip if already exists
        if output_file.exists():
            print(f"[{i+1}/{len(inputs)}] {source_id} - skipped (exists)")
            results["success"] += 1
            continue

        print(f"[{i+1}/{len(inputs)}] {source_id}...", end=" ", flush=True)

        try:
            enriched = call_openai_with_schema(client, system_prompt, normalized_input, schema)

            # Merge input fields with enriched output
            full_output = {**normalized_input, **enriched}

            with open(output_file, 'w') as f:
                json.dump(full_output, f, indent=2, ensure_ascii=False)

            print("✅")
            results["success"] += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            results["errors"] += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY: Test {args.test} - {config['description']}")
    print(f"{'='*70}")
    print(f"Total:   {results['total']}")
    print(f"Success: {results['success']} ✅")
    print(f"Errors:  {results['errors']} ❌")
    print(f"\nOutputs: {mode_output_dir}")


if __name__ == "__main__":
    main()
