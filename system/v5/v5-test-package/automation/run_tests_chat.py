#!/usr/bin/env python3
"""
PBH SIGNAL v5 - Internal Test Runner (Chat Completions API)

Simple test runner using Chat Completions with embedded dictionary.
For internal TCD use only - not for distribution to dev team.

Usage:
    python run_tests_chat.py                    # Run all tests
    python run_tests_chat.py --test ae_test_1  # Run single test
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: OpenAI package not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv package not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)


class ChatCompletionsTestRunner:
    """Simple test runner using Chat Completions API with embedded dictionary"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.client = None
        self.system_prompt_with_dict = None
        self.response_format = None

    def load_configuration(self):
        """Load OpenAI configuration and v5 enrichment files"""

        # Load environment variables
        env_path = self.base_dir / ".env"
        if not env_path.exists():
            print(f"❌ Error: .env file not found at {env_path}")
            print(f"   Copy .env.example to .env and add your API key")
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

        # Load system prompt
        prompt_path = self.base_dir.parent.parent / "enrichment" / "openai_assistant_system_prompt_v5.3.4.md"
        if not prompt_path.exists():
            print(f"❌ Error: System prompt not found at {prompt_path}")
            sys.exit(1)

        with open(prompt_path, 'r') as f:
            base_prompt = f.read()

        # Load dictionary
        dict_path = self.base_dir.parent.parent / "enrichment" / "PBH_SIGNAL_DICTIONARY_v5.txt"
        if not dict_path.exists():
            print(f"❌ Error: Dictionary not found at {dict_path}")
            sys.exit(1)

        with open(dict_path, 'r') as f:
            dictionary_content = f.read()

        # Combine prompt + dictionary
        # Replace "File Search" reference with embedded dictionary
        self.system_prompt_with_dict = base_prompt.replace(
            "Dictionary-based entity extraction using PBH SIGNAL DICTIONARY (File Search)",
            "Dictionary-based entity extraction using PBH SIGNAL DICTIONARY (embedded below)"
        )

        # Append dictionary to prompt
        self.system_prompt_with_dict += "\n\n" + "=" * 80 + "\n"
        self.system_prompt_with_dict += "PBH SIGNAL DICTIONARY (FOR ENTITY EXTRACTION)\n"
        self.system_prompt_with_dict += "=" * 80 + "\n\n"
        self.system_prompt_with_dict += dictionary_content

        # Load response format schema (wrapped version)
        schema_path = self.base_dir.parent.parent / "enrichment" / "openai_assistant_response_format_v5_wrapped.json"
        if not schema_path.exists():
            print(f"❌ Error: Response format not found at {schema_path}")
            sys.exit(1)

        with open(schema_path, 'r') as f:
            self.response_format = json.load(f)

        print("✅ Configuration loaded successfully")
        print(f"   System prompt length: {len(self.system_prompt_with_dict)} chars")
        print(f"   Dictionary embedded: ✓")
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
                        "content": self.system_prompt_with_dict
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

    def run_tests(self, test_filter: str = None):
        """Run enrichment tests"""

        # Create actual_outputs directory
        actual_dir = self.base_dir.parent / "actual_outputs"
        actual_dir.mkdir(parents=True, exist_ok=True)

        # Collect test files
        test_data_dir = self.base_dir.parent.parent / "enrichment-test-data-v5"

        if not test_data_dir.exists():
            print(f"❌ Error: enrichment-test-data-v5 directory not found at {test_data_dir}")
            sys.exit(1)

        # Collect from all test subdirectories
        test_dirs = [
            test_data_dir / "ae-test-cases",
            test_data_dir / "platform-coverage",
            test_data_dir / "edge-cases",
            test_data_dir / "dictionary-tests",
            test_data_dir / "classification-tests",
            test_data_dir / "flag-tests"
        ]

        test_files = []
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(sorted(test_dir.glob("*.json")))

        # Filter by test name if specified
        if test_filter:
            test_files = [f for f in test_files if test_filter in f.stem]
            if not test_files:
                print(f"❌ Error: No test files found matching '{test_filter}'")
                sys.exit(1)

        total_tests = len(test_files)
        print(f"🧪 Running {total_tests} enrichment tests...")
        print()

        successes = 0
        failures = 0
        start_time = time.time()

        for idx, test_file in enumerate(test_files, 1):
            test_name = test_file.stem
            print(f"[{idx}/{total_tests}] {test_name}...", end=" ", flush=True)

            try:
                # Load test input
                with open(test_file, 'r') as f:
                    test_input = json.load(f)

                # Run enrichment
                enriched_output = self.enrich_post(test_input)

                if enriched_output:
                    # Save output
                    output_path = actual_dir / f"{test_name}_actual.json"
                    with open(output_path, 'w') as f:
                        json.dump(enriched_output, f, indent=2)

                    print("✅")
                    successes += 1
                else:
                    print("❌ (API error)")
                    failures += 1

                # Rate limiting: delay between requests (30s for gpt-4.1 TPM limit)
                time.sleep(30.0)

            except Exception as e:
                print(f"❌ (Error: {str(e)})")
                failures += 1

        elapsed = time.time() - start_time

        print()
        print("=" * 60)
        print(f"✅ Testing complete!")
        print()
        print(f"Total: {total_tests} tests")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Time: {elapsed:.1f}s")
        print()
        print(f"Outputs saved to: {actual_dir}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run PBH SIGNAL v5 enrichment tests (Chat Completions)")
    parser.add_argument("--test", help="Run specific test (e.g., ae_test_1)")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    runner = ChatCompletionsTestRunner(base_dir)

    runner.load_configuration()
    runner.run_tests(test_filter=args.test)


if __name__ == "__main__":
    main()
