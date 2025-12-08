#!/usr/bin/env python3
"""
PBH SIGNAL v6 - Test Runner (Chat Completions API)

Runs v6 enrichment tests using Chat Completions with the v6 system prompt
and embedded dictionary.

Usage:
    python run_tests_v6.py                         # Run all 45 tests
    python run_tests_v6.py --source-id t3_xyz      # Run single test
    python run_tests_v6.py --limit 5               # Run first 5 tests
    python run_tests_v6.py --delay 10              # 10 second delay between tests
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: OpenAI package not installed")
    print("   Run: pip install openai python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv package not installed")
    print("   Run: pip install python-dotenv")
    sys.exit(1)


class V6TestRunner:
    """Test runner using Chat Completions API with v6 configuration"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.client = None
        self.system_prompt = None
        self.response_format = None

    def load_configuration(self):
        """Load OpenAI configuration and v6 enrichment files"""

        # Load environment variables - search up to project root
        env_path = self.base_dir / ".env"
        if not env_path.exists():
            # Try parent directories (testing -> v6 -> system -> project_root)
            search_dirs = [
                self.base_dir.parent,           # v6/
                self.base_dir.parent.parent,    # system/
                self.base_dir.parent.parent.parent  # project root
            ]
            for parent in search_dirs:
                alt_env = parent / ".env"
                if alt_env.exists():
                    env_path = alt_env
                    break

        if not env_path.exists():
            print(f"❌ Error: .env file not found")
            print(f"   Create .env with OPENAI_API_KEY=your-key")
            print(f"   Searched: {self.base_dir} and parent directories")
            sys.exit(1)

        load_dotenv(env_path)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"❌ Error: OPENAI_API_KEY not found in .env file")
            sys.exit(1)

        # Initialize OpenAI client
        org_id = os.getenv("OPENAI_ORG_ID")
        if org_id:
            self.client = OpenAI(api_key=api_key, organization=org_id)
        else:
            self.client = OpenAI(api_key=api_key)

        # Load v6 system prompt with embedded dictionary
        prompt_path = self.base_dir.parent / "enrichment" / "openai_assistant_system_prompt_v6_with_dictionary.md"
        if not prompt_path.exists():
            print(f"❌ Error: v6 system prompt not found at {prompt_path}")
            sys.exit(1)

        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()

        # Load v6 response format schema
        schema_path = self.base_dir.parent / "enrichment" / "openai_assistant_response_format_v6.json"
        if not schema_path.exists():
            print(f"❌ Error: v6 response format not found at {schema_path}")
            sys.exit(1)

        with open(schema_path, 'r') as f:
            schema_file = json.load(f)

        # The schema file already has name, strict, schema structure
        # Wrap for Chat Completions API
        self.response_format = {
            "type": "json_schema",
            "json_schema": schema_file
        }

        print("✅ Configuration loaded successfully")
        print(f"   System prompt length: {len(self.system_prompt):,} chars")
        print(f"   Response schema: v6 enrichment format")
        print()

    def enrich_post(self, normalized_data: dict) -> dict:
        """Call Chat Completions API with structured output"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Enrich this normalized post:\n\n{json.dumps(normalized_data, indent=2)}"
                    }
                ],
                response_format=self.response_format
            )

            # Parse response
            enriched_data = json.loads(response.choices[0].message.content)
            return enriched_data

        except Exception as e:
            print(f"\n   ❌ API Error: {type(e).__name__}")
            print(f"      {str(e)}")
            return None

    def run_tests(self, source_id_filter: str = None, limit: int = None, delay: float = 30.0):
        """Run enrichment tests"""

        # Create enriched_outputs directory
        output_dir = self.base_dir / "enriched_outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find normalized input files
        input_dir = self.base_dir / "normalized_inputs"
        if not input_dir.exists():
            print(f"❌ Error: normalized_inputs directory not found")
            print(f"   Run csv_to_normalized.py first")
            sys.exit(1)

        input_files = sorted(input_dir.glob("*.json"))

        # Filter if specified
        if source_id_filter:
            input_files = [f for f in input_files if source_id_filter in f.stem]
            if not input_files:
                print(f"❌ Error: No input files found matching '{source_id_filter}'")
                sys.exit(1)

        # Limit if specified
        if limit:
            input_files = input_files[:limit]

        total_tests = len(input_files)
        print(f"🧪 Running {total_tests} v6 enrichment tests...")
        print(f"   Delay between tests: {delay}s")
        print()

        successes = 0
        failures = 0
        start_time = time.time()

        for idx, input_file in enumerate(input_files, 1):
            source_id = input_file.stem
            print(f"[{idx}/{total_tests}] {source_id}...", end=" ", flush=True)

            try:
                # Load normalized input
                with open(input_file, 'r') as f:
                    normalized_data = json.load(f)

                # Run enrichment
                enriched_output = self.enrich_post(normalized_data)

                if enriched_output:
                    # Save output
                    output_path = output_dir / f"{source_id}_enriched.json"
                    with open(output_path, 'w') as f:
                        json.dump(enriched_output, f, indent=2)

                    # Quick preview of key fields
                    rel = enriched_output.get('relevance_label', '?')
                    ctx = enriched_output.get('bariatric_context', '?')
                    print(f"✅ (relevance={rel}, context={ctx})")
                    successes += 1
                else:
                    print("❌ (API error)")
                    failures += 1

                # Rate limiting
                if idx < total_tests:  # Don't delay after last test
                    time.sleep(delay)

            except Exception as e:
                print(f"❌ (Error: {str(e)})")
                failures += 1

        elapsed = time.time() - start_time

        print()
        print("=" * 70)
        print(f"✅ v6 Testing complete!")
        print()
        print(f"Total: {total_tests} tests")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print()
        print(f"Outputs saved to: {output_dir}")
        print()
        print("Next step: Run score_results_v6.py to analyze results")
        print("=" * 70)

        return successes, failures


def main():
    parser = argparse.ArgumentParser(description="Run PBH SIGNAL v6 enrichment tests")
    parser.add_argument("--source-id", help="Run specific source_id only")
    parser.add_argument("--limit", type=int, help="Limit number of tests to run")
    parser.add_argument("--delay", type=float, default=30.0,
                        help="Delay between API calls in seconds (default: 30)")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    runner = V6TestRunner(base_dir)

    runner.load_configuration()
    runner.run_tests(
        source_id_filter=args.source_id,
        limit=args.limit,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
