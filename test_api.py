"""
Test script to verify all API endpoints work correctly.
Run this after starting the Flask app to ensure everything is functioning.
"""

import requests
import json

# Base URL - change this to your deployed URL when testing on Render
BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_get_authors():
    """Test GET /authors"""
    response = requests.get(f"{BASE_URL}/authors")
    print_response("TEST 1: GET /authors", response)
    
    # Verify expected balances
    data = response.json()
    assert data[0]["total_earnings"] == 3825, "Priya's earnings should be 3825"
    assert data[1]["total_earnings"] == 9975, "Rahul's earnings should be 9975"
    assert data[2]["total_earnings"] == 400, "Anita's earnings should be 400"
    print("✅ All author balances are correct!")

def test_get_author_detail():
    """Test GET /authors/1"""
    response = requests.get(f"{BASE_URL}/authors/1")
    print_response("TEST 2: GET /authors/1 (Priya's details)", response)
    
    data = response.json()
    assert data["total_books"] == 2, "Priya should have 2 books"
    assert data["email"] == "priya@email.com", "Email should match"
    print("✅ Author details are correct!")

def test_get_author_sales():
    """Test GET /authors/1/sales"""
    response = requests.get(f"{BASE_URL}/authors/1/sales")
    print_response("TEST 3: GET /authors/1/sales", response)
    
    data = response.json()
    assert len(data) == 3, "Priya should have 3 sales records"
    assert data[0]["sale_date"] > data[1]["sale_date"], "Sales should be sorted by date (newest first)"
    print("✅ Sales data is correct and sorted!")

def test_create_withdrawal_success():
    """Test POST /withdrawals - Success case"""
    payload = {
        "author_id": 1,
        "amount": 2000
    }
    response = requests.post(f"{BASE_URL}/withdrawals", json=payload)
    print_response("TEST 4: POST /withdrawals (Success)", response)
    
    data = response.json()
    assert response.status_code == 201, "Should return 201 Created"
    assert data["amount"] == 2000, "Amount should be 2000"
    assert data["status"] == "pending", "Status should be pending"
    assert data["new_balance"] == 1825, "New balance should be 1825 (3825 - 2000)"
    print("✅ Withdrawal created successfully!")

def test_create_withdrawal_minimum_amount():
    """Test POST /withdrawals - Amount less than 500"""
    payload = {
        "author_id": 1,
        "amount": 400
    }
    response = requests.post(f"{BASE_URL}/withdrawals", json=payload)
    print_response("TEST 5: POST /withdrawals (Amount < 500)", response)
    
    assert response.status_code == 400, "Should return 400 Bad Request"
    assert "Minimum withdrawal" in response.json()["error"]
    print("✅ Minimum amount validation works!")

def test_create_withdrawal_insufficient_balance():
    """Test POST /withdrawals - Insufficient balance"""
    payload = {
        "author_id": 3,  # Anita has only 400
        "amount": 500
    }
    response = requests.post(f"{BASE_URL}/withdrawals", json=payload)
    print_response("TEST 6: POST /withdrawals (Insufficient balance)", response)
    
    assert response.status_code == 400, "Should return 400 Bad Request"
    assert "Insufficient balance" in response.json()["error"]
    print("✅ Balance validation works!")

def test_create_withdrawal_author_not_found():
    """Test POST /withdrawals - Author not found"""
    payload = {
        "author_id": 999,
        "amount": 1000
    }
    response = requests.post(f"{BASE_URL}/withdrawals", json=payload)
    print_response("TEST 7: POST /withdrawals (Author not found)", response)
    
    assert response.status_code == 404, "Should return 404 Not Found"
    assert "Author not found" in response.json()["error"]
    print("✅ Author validation works!")

def test_get_author_withdrawals():
    """Test GET /authors/1/withdrawals"""
    response = requests.get(f"{BASE_URL}/authors/1/withdrawals")
    print_response("TEST 8: GET /authors/1/withdrawals", response)
    
    data = response.json()
    assert len(data) >= 1, "Priya should have at least 1 withdrawal from previous test"
    print("✅ Withdrawal history retrieved successfully!")

def test_get_nonexistent_author():
    """Test GET /authors/999 - Not found"""
    response = requests.get(f"{BASE_URL}/authors/999")
    print_response("TEST 9: GET /authors/999 (Not found)", response)
    
    assert response.status_code == 404, "Should return 404 Not Found"
    print("✅ 404 handling works!")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("BOOKLEAF ROYALTY API - TEST SUITE")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the Flask app is running!")
    
    try:
        # Test if API is running
        response = requests.get(BASE_URL)
        print("\n✅ API is running!")
        
        # Run all tests
        test_get_authors()
        test_get_author_detail()
        test_get_author_sales()
        test_create_withdrawal_success()
        test_create_withdrawal_minimum_amount()
        test_create_withdrawal_insufficient_balance()
        test_create_withdrawal_author_not_found()
        test_get_author_withdrawals()
        test_get_nonexistent_author()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nYour API is ready for deployment!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the Flask app is running on port 5000")
        print("Run: python app.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()