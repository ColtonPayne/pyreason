#!/usr/bin/env python3
"""
Script to run both disable_jit and dont_disable_jit tests with unified coverage.
Since JIT settings are global and affect the entire Python session,
we run each test suite in a separate subprocess but combine coverage data.
"""

import subprocess
import sys
import os
import tempfile

def run_tests_with_coverage(test_path, description, coverage_file):
    """Run pytest with coverage on the given path."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")

    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    # Set coverage data file via environment variable
    env["COVERAGE_FILE"] = coverage_file

    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--cov=pyreason",
        "--cov-append",
        "--cov-report="  # Disable individual reports, we'll generate combined one
    ]
    result = subprocess.run(cmd, env=env, cwd=os.getcwd())

    return result.returncode

def main():
    """Run all test suites with unified coverage reporting."""
    print("Running PyReason Unit Tests with Coverage")
    print("This runs disable_jit and dont_disable_jit tests separately to avoid JIT conflicts.")

    # Create temporary coverage file
    with tempfile.NamedTemporaryFile(suffix='.coverage', delete=False) as f:
        coverage_file = f.name

    try:
        results = {}

        # Run disable_jit tests
        results["disable_jit"] = run_tests_with_coverage(
            "tests/unit/disable_jit/",
            "disable_jit tests",
            coverage_file
        )

        # Run dont_disable_jit tests
        results["dont_disable_jit"] = run_tests_with_coverage(
            "tests/unit/dont_disable_jit/",
            "dont_disable_jit tests",
            coverage_file
        )

        # Generate combined coverage report
        print(f"\n{'='*60}")
        print("Generating Combined Coverage Report")
        print(f"{'='*60}")

        coverage_cmd = [
            sys.executable, "-m", "coverage", "report",
            f"--data-file={coverage_file}"
        ]
        subprocess.run(coverage_cmd, cwd=os.getcwd())

        # Also generate HTML report
        html_cmd = [
            sys.executable, "-m", "coverage", "html",
            f"--data-file={coverage_file}",
            "--directory=htmlcov"
        ]
        subprocess.run(html_cmd, cwd=os.getcwd())
        print("\nHTML coverage report generated in htmlcov/")

        # Summary
        print(f"\n{'='*60}")
        print("Test Results Summary")
        print(f"{'='*60}")

        all_passed = True
        for suite, exit_code in results.items():
            status = "PASSED" if exit_code == 0 else "FAILED"
            print(f"{suite}: {status}")
            if exit_code != 0:
                all_passed = False

        if all_passed:
            print("\n✅ All test suites passed!")
            return 0
        else:
            print("\n❌ Some test suites failed!")
            return 1

    finally:
        # Clean up temporary coverage file
        if os.path.exists(coverage_file):
            os.unlink(coverage_file)

if __name__ == "__main__":
    sys.exit(main())