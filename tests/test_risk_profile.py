"""Simple tests for risk_profile module"""
from src.risk_profile import calculate_risk_score, get_risk_profile

def test_score_calculation():
    """Test basic math of score calculation"""
    answers = [1, 2, 3, 4]  # 4 questions
    score = calculate_risk_score(answers)
    # Expected: ((1+2+3+4 - 4) / (16 - 4)) * 100 = 50.0
    assert score == 50.0, f"Expected 50.0, got {score}"
    print("✓ Score calculation works")

def test_conservative_profile():
    """Test Conservative risk profile (0-35)"""
    profile = get_risk_profile(25)  # Score in conservative range
    assert profile == "Conservative"
    print("✓ Conservative profile correct")

def test_moderate_profile():
    """Test Moderate risk profile (36-70)"""
    profile = get_risk_profile(50)
    assert profile == "Moderate"
    print("✓ Moderate profile correct")

def test_aggressive_profile():
    """Test Aggressive risk profile (71-100)"""
    profile = get_risk_profile(85)
    assert profile == "Aggressive"
    print("✓ Aggressive profile correct")

# Run tests if file is executed directly
if __name__ == "__main__":
    test_score_calculation()
    test_conservative_profile()
    test_moderate_profile()
    test_aggressive_profile()
    print("\n✅ All tests passed!")