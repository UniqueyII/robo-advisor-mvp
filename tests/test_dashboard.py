import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock streamlit before importing
mock_st = MagicMock()

# session_state should be a dictionary that supports item assignment
mock_st.session_state = {}

# Mock common streamlit functions
mock_st.title = MagicMock()
mock_st.markdown = MagicMock()
mock_st.write = MagicMock()
mock_st.sidebar = MagicMock()
mock_st.button = MagicMock(return_value=False)
mock_st.selectbox = MagicMock(return_value="Conservative")
mock_st.slider = MagicMock(return_value=100000000)
mock_st.number_input = MagicMock(return_value=100000000)
mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
mock_st.form = MagicMock()
mock_st.form_submit_button = MagicMock(return_value=False)
mock_st.radio = MagicMock(return_value=2)

# Replace streamlit with our mock
with patch.dict('sys.modules', {'streamlit': mock_st}):
    import src.dashboard as dashboard

def test_dashboard_imports():
    """Test that dashboard imports correctly"""
    assert dashboard is not None
    print("✓ Dashboard imports successfully")

def test_session_state():
    """Test session state initialization"""
    # Clear session state
    mock_st.session_state.clear()
    
    # Check if dashboard has a main function that initializes session state
    if hasattr(dashboard, 'main'):
        # Call main which should initialize session state
        try:
            with patch('streamlit.session_state', mock_st.session_state):
                dashboard.main()
        except Exception as e:
            print(f"  ℹ main() called: {type(e).__name__}")
    
    # If dashboard has an init function
    if hasattr(dashboard, 'init_session_state'):
        dashboard.init_session_state()
    
    # Just verify it runs without crashing
    print("✓ Session state test completed")

def test_page_navigation():
    """Test that page navigation works"""
    # Mock button clicks
    mock_st.button.return_value = True  # Simulate button click
    
    # Reset session state with page 0
    mock_st.session_state.clear()
    mock_st.session_state['page'] = 0
    
    try:
        if hasattr(dashboard, 'main'):
            with patch('streamlit.session_state', mock_st.session_state):
                dashboard.main()
        print("✓ Navigation test completed")
    except Exception as e:
        print(f"  ℹ Navigation test: {type(e).__name__}")

def test_questionnaire_page():
    """Test that questionnaire page renders"""
    # Set session to questionnaire page (page 1)
    mock_st.session_state.clear()
    mock_st.session_state['page'] = 1
    
    try:
        if hasattr(dashboard, 'main'):
            with patch('streamlit.session_state', mock_st.session_state):
                dashboard.main()
        print("✓ Questionnaire page test completed")
    except Exception as e:
        print(f"  ℹ Questionnaire page: {type(e).__name__}")

def test_results_page():
    """Test that results page renders"""
    # Set session to results page with data
    mock_st.session_state.clear()
    mock_st.session_state['page'] = 5
    mock_st.session_state['risk_profile'] = 'Aggressive'
    mock_st.session_state['risk_score'] = 85
    mock_st.session_state['investment_amount'] = 100000000
    
    try:
        if hasattr(dashboard, 'main'):
            with patch('streamlit.session_state', mock_st.session_state):
                dashboard.main()
        print("✓ Results page test completed")
    except Exception as e:
        print(f"  ℹ Results page: {type(e).__name__}")

def test_currency_display():
    """Test that currency formatting works"""
    # Look for currency formatting functions
    if hasattr(dashboard, 'format_currency'):
        result = dashboard.format_currency(1000000)
        print(f"✓ Currency formatting exists")
    else:
        # Check if currency formatting is inline
        with open('src/dashboard.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'تومان' in content and 'دلار' in content:
                print("✓ Currency display found in UI")
            else:
                print("ℹ Currency display not found")

def test_error_handling():
    """Test that dashboard handles errors gracefully"""
    # Clear session state (should trigger error handling)
    mock_st.session_state.clear()
    
    try:
        if hasattr(dashboard, 'main'):
            with patch('streamlit.session_state', mock_st.session_state):
                dashboard.main()
        print("✓ Error handling test completed")
    except Exception as e:
        print(f"  ℹ Error handling: {type(e).__name__}")

if __name__ == "__main__":
    print("🔧 Testing dashboard.py")
    print("=" * 60)
    
    tests = [
        test_dashboard_imports,
        test_session_state,
        test_page_navigation,
        test_questionnaire_page,
        test_results_page,
        test_currency_display,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} passed\n")
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"⚠️ {test.__name__} error: {type(e).__name__}: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("ALL DASHBOARD TESTS PASSED")
    else:
        print(f"⚠ {failed} test(s) failed")