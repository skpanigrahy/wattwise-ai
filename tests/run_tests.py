#!/usr/bin/env python3
"""
Test runner for WattWise AI
"""

import os
import sys
import subprocess
import argparse

def run_tests(test_type="all", coverage=True, verbose=True):
    """Run tests with specified options"""
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Add backend to Python path
    backend_path = os.path.join(project_root, "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Set testing environment
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test_wattwise.db"
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add test selection based on type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.append("tests/test_api.py")
    elif test_type == "scheduler":
        cmd.append("tests/test_scheduler.py")
    elif test_type == "assistant":
        cmd.append("tests/test_assistant.py")
    elif test_type == "models":
        cmd.append("tests/test_models.py")
    else:  # all
        cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run WattWise AI tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "api", "scheduler", "assistant", "models"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run tests in quiet mode"
    )
    
    args = parser.parse_args()
    
    print("🧪 WattWise AI Test Runner")
    print(f"Test type: {args.type}")
    print(f"Coverage: {'disabled' if args.no_coverage else 'enabled'}")
    print(f"Verbose: {'disabled' if args.quiet else 'enabled'}")
    print("=" * 50)
    
    exit_code = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

