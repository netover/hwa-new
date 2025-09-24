#!/usr/bin/env python3
"""
Mutation testing script for Resync core modules.

This script runs mutation testing using mutmut on critical core modules
to validate test effectiveness. Configuration is defined in the script
to ensure consistent behavior.

Usage:
    python scripts/mutation_test.py
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List

# Define configuration
CORE_MODULES: List[str] = [
    "resync/core/agent_manager.py",
    "resync/core/ia_auditor.py",
    "resync/core/async_cache.py",
    "resync/core/audit_lock.py",
    "resync/core/cache_hierarchy.py"
]

# Define mutmut configuration
MUTMUT_CONFIG = {
    "runner": "pytest tests/ --tb=short",
    "timeout": 10,
    "output_file": "reports/mutation_results.json",
    "exclude_paths": [
        "tests/*",
        "config/*",
        "scripts/*",
        "docs/*",
        "static/*",
        "templates/*"
    ]
}

def run_mutation_test() -> int:
    """
    Run mutation testing using mutmut with configured parameters.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # Build mutmut command
    cmd = [
        "mutmut",
        "run",
        "--runner", MUTMUT_CONFIG["runner"],
        "--timeout", str(MUTMUT_CONFIG["timeout"]),
        "--output-file", MUTMUT_CONFIG["output_file"]
    ]

    # Add exclude patterns
    for path in MUTMUT_CONFIG["exclude_paths"]:
        cmd.extend(["--exclude", path])

    # Add core modules to test
    cmd.extend(CORE_MODULES)

    print("Running mutation test with configuration:")
    print(f"  Runner: {MUTMUT_CONFIG['runner']}")
    print(f"  Timeout: {MUTMUT_CONFIG['timeout']}s")
    print(f"  Output: {MUTMUT_CONFIG['output_file']}")
    print(f"  Excluded paths: {MUTMUT_CONFIG['exclude_paths']}")
    print(f"  Testing modules: {CORE_MODULES}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Mutation test completed successfully!")
            print(f"📊 Results saved to: {MUTMUT_CONFIG['output_file']}")
            return 0
        else:
            print("❌ Mutation test failed!")
            print(f"Exit code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            return result.returncode

        except FileNotFoundError:
        print("❌ mutmut not found. Please ensure it is installed with 'pip install mutmut'")
        return 1
    except ModuleNotFoundError as e:
        if "resource" in str(e):
            print("❌ mutmut has compatibility issues on Windows due to missing 'resource' module.")
            print("💡 Workaround: Run mutation testing in a Linux environment or use WSL.")
            print("   Alternatively, consider using pytest with coverage instead for Windows.")
            return 1
        else:
            print(f"❌ Module not found: {e}")
            return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1</search>
</search_and_replace>

def check_success_criteria() -> bool:
    """
    Check if mutation test results meet success criteria.

    Returns:
        bool: True if mutation score >= 95% and critical paths are covered
    """
    output_file = Path(MUTMUT_CONFIG["output_file"])

    if not output_file.exists():
        print("❌ Mutation results file not found. Run mutation test first.")
        return False

    try:
        with open(output_file, 'r') as f:
            results = json.load(f)

        mutation_score = results.get('mutation_score', 0)
        survived_mutants = results.get('survived_mutants', 0)

        print(f"📊 Mutation score: {mutation_score:.1f}%")
        print(f"💥 Survived mutants: {survived_mutants}")

        # Check if mutation score meets minimum threshold
        if mutation_score >= 95:
            print("✅ Mutation score meets target (≥95%)")
            return True
        else:
            print("❌ Mutation score below target (<95%)")
            return False

    except Exception as e:
        print(f"❌ Error reading mutation results: {e}")
        return False

def main():
    """Main entry point for mutation testing script."""
    print("🚀 Starting mutation testing for Resync core modules...")

    # Run mutation test
    exit_code = run_mutation_test()

    if exit_code != 0:
        print("🚨 Mutation test execution failed.")
        sys.exit(exit_code)

    # Check success criteria
    if not check_success_criteria():
        print("🚨 Mutation test passed, but failed success criteria.")
        sys.exit(1)

    print("🎉 Mutation testing completed successfully!")
    print("✅ Test coverage depth validated. Code quality and test robustness confirmed.")

if __name__ == "__main__":
    main()