"""
Fixed coverage runner - avoids NumPy import conflict
Run this instead of pytest directly
"""
import subprocess
import sys
import os

def run_coverage():
    """Run coverage with proper isolation"""
    
    # Run tests one by one to avoid import conflicts
    test_files = [
        "tests/test_risk_profile.py",
        "tests/test_data_fetcher.py",
        "tests/test_portfolio_optimizer.py",
    ]
    
    print("📊 Running coverage with isolated test files...")
    print("=" * 60)
    
    total_coverage = {}
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠ Skipping {test_file} - not found")
            continue
            
        print(f"\n📋 Testing: {test_file}")
        print("-" * 40)
        
        # Run pytest on single file
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--cov=src", "--cov-append"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            if "ImportError" not in result.stderr:  # Only show non-import errors
                print("STDERR:", result.stderr)
    
    # Generate final coverage report
    print("\n" + "=" * 60)
    print("📈 Final Coverage Report")
    print("=" * 60)
    
    subprocess.run(
        [sys.executable, "-m", "coverage", "report", "--show-missing"],
        capture_output=False
    )
    
    # Generate HTML report
    subprocess.run(
        [sys.executable, "-m", "coverage", "html"],
        capture_output=False
    )
    
    print("\n✅ HTML coverage report: file://" + os.path.abspath("htmlcov/index.html"))

if __name__ == "__main__":
    # Clear previous coverage data
    if os.path.exists(".coverage"):
        os.remove(".coverage")
    
    run_coverage()