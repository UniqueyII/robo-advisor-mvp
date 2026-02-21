"""
Test runner for Robo-Advisor MVP
Run all tests with: python run_tests.py
"""
import subprocess
import sys
import os

def run_tests():
    """Run all test files"""
    print("🚀 Running Robo-Advisor MVP Test Suite")
    print("=" * 50)
    
    test_files = [
        "tests/test_risk_profile.py",
        "tests/test_data_fetcher.py",
        # Add more as we create them
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Testing: {test_file}")
            print("-" * 40)
            
            # Run pytest on this file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True
            )
            
            # Print output
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Check if tests passed
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
            else:
                print(f"❌ {test_file} - FAILED")
                all_passed = False
        else:
            print(f"⚠  {test_file} - Not found (skipping)")
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠  SOME TESTS FAILED")
    
    return all_passed

def run_coverage():
    """Generate coverage report"""
    print("\n📊 Generating Coverage Report...")
    print("-" * 40)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/",
         "--cov=src",
         "--cov-report=term-missing",
         "--cov-report=html"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if os.path.exists("htmlcov/index.html"):
        print("\n📈 HTML coverage report: file://" + os.path.abspath("htmlcov/index.html"))
    
    return result.returncode == 0

if __name__ == "__main__":
    # Run tests
    tests_ok = run_tests()
    
    # Only run coverage if tests passed
    if tests_ok:
        run_coverage()
        
        # Final message
        print("\n" + "=" * 50)
        print("📋 Next Steps:")
        print("1. View coverage report: htmlcov/index.html")
        print("2. Add tests for portfolio_optimizer.py")
        print("3. Set up GitHub Actions for CI/CD")
        print("=" * 50)
    else:
        print("\n⚠️  Fix failing tests before generating coverage report.")
        sys.exit(1)