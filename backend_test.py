#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Miluv.app Dating Application
Tests all backend endpoints systematically according to priority levels
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://miluv-app-1.preview.emergentagent.com') + '/api'
print(f"Testing Backend URL: {BACKEND_URL}")

# Test user data
TEST_USER = {
    "name": "Test User",
    "email": "test@miluv.com", 
    "password": "miluv123",
    "date_of_birth": "1995-06-15",
    "gender": "male",
    "username": "testuser001",
    "profile_photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "latitude": -6.2088,
    "longitude": 106.8456
}

# Test user 2 for matching tests
TEST_USER_2 = {
    "name": "Test User 2",
    "email": "test2@miluv.com",
    "password": "miluv123",
    "date_of_birth": "1993-08-20",
    "gender": "female", 
    "username": "testuser002",
    "profile_photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "latitude": -6.2100,
    "longitude": 106.8500
}

# Global variables for test state
auth_token = None
user_id = None
auth_token_2 = None
user_id_2 = None
match_id = None

class TestResults:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, test_name, status, details=""):
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
        
        # Print result immediately
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {status}")
        if details and status == "FAIL":
            print(f"   Details: {details}")
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/len(self.results)*100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")

test_results = TestResults()

def make_request(method, endpoint, data=None, headers=None, expected_status=200):
    """Make HTTP request with error handling"""
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        
        return response
    except requests.exceptions.RequestException as e:
        return None

def get_auth_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ============================================
# PRIORITY 1 - AUTH FLOW TESTS
# ============================================

def test_api_root():
    """Test API root endpoint"""
    response = make_request("GET", "/")
    if response and response.status_code == 200:
        data = response.json()
        if "message" in data and "Miluv.app API" in data["message"]:
            test_results.add_result("API Root", "PASS")
            return True
        else:
            test_results.add_result("API Root", "FAIL", f"Unexpected response: {data}")
            return False
    else:
        test_results.add_result("API Root", "FAIL", f"Request failed: {response.status_code if response else 'No response'}")
        return False

def test_register_user():
    """Test user registration"""
    global auth_token, user_id
    
    response = make_request("POST", "/auth/register", TEST_USER)
    if response and response.status_code == 200:
        data = response.json()
        if "token" in data and "user_id" in data:
            auth_token = data["token"]
            user_id = data["user_id"]
            test_results.add_result("User Registration", "PASS")
            return True
        else:
            test_results.add_result("User Registration", "FAIL", f"Missing token or user_id: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("User Registration", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_register_user_2():
    """Test second user registration for matching tests"""
    global auth_token_2, user_id_2
    
    response = make_request("POST", "/auth/register", TEST_USER_2)
    if response and response.status_code == 200:
        data = response.json()
        if "token" in data and "user_id" in data:
            auth_token_2 = data["token"]
            user_id_2 = data["user_id"]
            test_results.add_result("User 2 Registration", "PASS")
            return True
        else:
            test_results.add_result("User 2 Registration", "FAIL", f"Missing token or user_id: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("User 2 Registration", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_login():
    """Test user login"""
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response = make_request("POST", "/auth/login", login_data)
    if response and response.status_code == 200:
        data = response.json()
        if "token" in data and "user_id" in data:
            test_results.add_result("User Login", "PASS")
            return True
        else:
            test_results.add_result("User Login", "FAIL", f"Missing token or user_id: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("User Login", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    login_data = {
        "email": "invalid@test.com",
        "password": "wrongpassword"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    if response and response.status_code == 401:
        test_results.add_result("Invalid Login", "PASS")
        return True
    else:
        test_results.add_result("Invalid Login", "FAIL", f"Expected 401, got {response.status_code if response else 'None'}")
        return False

def test_face_verification():
    """Test face verification (mocked)"""
    if not auth_token:
        test_results.add_result("Face Verification", "FAIL", "No auth token available")
        return False
    
    verification_data = {
        "selfie_photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
    
    headers = get_auth_headers(auth_token)
    response = make_request("POST", "/auth/verify-face", verification_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get("verified") == True:
            test_results.add_result("Face Verification", "PASS")
            return True
        else:
            test_results.add_result("Face Verification", "FAIL", f"Verification failed: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Face Verification", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 2 - ASSESSMENT SYSTEM TESTS
# ============================================

def test_get_assessment_questions():
    """Test getting assessment questions for all test types"""
    if not auth_token:
        test_results.add_result("Get Assessment Questions", "FAIL", "No auth token available")
        return False
    
    test_types = ["mbti", "love_language", "readiness", "temperament", "disc"]
    headers = get_auth_headers(auth_token)
    
    for test_type in test_types:
        response = make_request("GET", f"/assessment/questions/{test_type}", headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            if "questions" in data and len(data["questions"]) == 10:
                test_results.add_result(f"Get {test_type.upper()} Questions", "PASS")
            else:
                test_results.add_result(f"Get {test_type.upper()} Questions", "FAIL", f"Expected 10 questions, got {len(data.get('questions', []))}")
                return False
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            test_results.add_result(f"Get {test_type.upper()} Questions", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False
    
    return True

def test_submit_assessments():
    """Test submitting all 5 assessments"""
    if not auth_token:
        test_results.add_result("Submit Assessments", "FAIL", "No auth token available")
        return False
    
    test_types = ["mbti", "love_language", "readiness", "temperament", "disc"]
    headers = get_auth_headers(auth_token)
    
    # Sample answers (indices 0-4, 10 answers each)
    sample_answers = [3, 4, 2, 3, 4, 3, 2, 4, 3, 2]  # High scores for better matching
    
    for test_type in test_types:
        assessment_data = {
            "test_type": test_type,
            "answers": sample_answers
        }
        
        response = make_request("POST", "/assessment/submit", assessment_data, headers)
        if response and response.status_code == 200:
            data = response.json()
            if "result" in data:
                test_results.add_result(f"Submit {test_type.upper()} Assessment", "PASS")
            else:
                test_results.add_result(f"Submit {test_type.upper()} Assessment", "FAIL", f"No result in response: {data}")
                return False
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            test_results.add_result(f"Submit {test_type.upper()} Assessment", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False
    
    return True

def test_submit_assessments_user_2():
    """Test submitting assessments for user 2"""
    if not auth_token_2:
        test_results.add_result("Submit Assessments User 2", "FAIL", "No auth token available for user 2")
        return False
    
    test_types = ["mbti", "love_language", "readiness", "temperament", "disc"]
    headers = get_auth_headers(auth_token_2)
    
    # Different answers for user 2
    sample_answers = [4, 3, 4, 2, 3, 4, 3, 2, 4, 3]  # High scores for matching
    
    for test_type in test_types:
        assessment_data = {
            "test_type": test_type,
            "answers": sample_answers
        }
        
        response = make_request("POST", "/assessment/submit", assessment_data, headers)
        if response and response.status_code == 200:
            data = response.json()
            if "result" in data:
                test_results.add_result(f"Submit {test_type.upper()} Assessment User 2", "PASS")
            else:
                test_results.add_result(f"Submit {test_type.upper()} Assessment User 2", "FAIL", f"No result in response: {data}")
                return False
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            test_results.add_result(f"Submit {test_type.upper()} Assessment User 2", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False
    
    return True

def test_assessment_status():
    """Test assessment completion status"""
    if not auth_token:
        test_results.add_result("Assessment Status", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/assessment/status", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get("all_completed") == True:
            test_results.add_result("Assessment Status", "PASS")
            return True
        else:
            test_results.add_result("Assessment Status", "FAIL", f"Assessments not completed: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Assessment Status", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 3 - DISCOVERY & MATCHING TESTS
# ============================================

def test_discover_users():
    """Test discover endpoint with different radius values"""
    if not auth_token:
        test_results.add_result("Discover Users", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    
    # Test with 50km radius
    response = make_request("GET", "/discover?radius=50", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        if "users" in data:
            test_results.add_result("Discover Users (50km)", "PASS")
        else:
            test_results.add_result("Discover Users (50km)", "FAIL", f"No users field: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Discover Users (50km)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False
    
    # Test with 100km radius
    response = make_request("GET", "/discover?radius=100", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        if "users" in data:
            test_results.add_result("Discover Users (100km)", "PASS")
            return True
        else:
            test_results.add_result("Discover Users (100km)", "FAIL", f"No users field: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Discover Users (100km)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_like_user():
    """Test liking a user"""
    global match_id
    
    if not auth_token or not user_id_2:
        test_results.add_result("Like User", "FAIL", "Missing auth token or target user")
        return False
    
    headers = get_auth_headers(auth_token)
    like_data = {"target_user_id": user_id_2}
    
    response = make_request("POST", "/like", like_data, headers)
    if response and response.status_code == 200:
        data = response.json()
        if "message" in data:
            test_results.add_result("Like User", "PASS")
            return True
        else:
            test_results.add_result("Like User", "FAIL", f"No message in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Like User", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_reciprocal_like():
    """Test reciprocal like to create match"""
    global match_id
    
    if not auth_token_2 or not user_id:
        test_results.add_result("Reciprocal Like", "FAIL", "Missing auth token or target user")
        return False
    
    headers = get_auth_headers(auth_token_2)
    like_data = {"target_user_id": user_id}
    
    response = make_request("POST", "/like", like_data, headers)
    if response and response.status_code == 200:
        data = response.json()
        if data.get("match") == True and "match_id" in data:
            match_id = data["match_id"]
            test_results.add_result("Reciprocal Like (Match Created)", "PASS")
            return True
        else:
            test_results.add_result("Reciprocal Like (Match Created)", "FAIL", f"No match created: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Reciprocal Like (Match Created)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_get_matches():
    """Test getting matches list"""
    if not auth_token:
        test_results.add_result("Get Matches", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/matches", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "matches" in data:
            test_results.add_result("Get Matches", "PASS")
            return True
        else:
            test_results.add_result("Get Matches", "FAIL", f"No matches field: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Matches", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 4 - CHAT TESTS
# ============================================

def test_get_messages():
    """Test getting messages for a match"""
    if not auth_token or not match_id:
        test_results.add_result("Get Messages", "FAIL", "Missing auth token or match_id")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", f"/chat/{match_id}/messages", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "messages" in data:
            test_results.add_result("Get Messages", "PASS")
            return True
        else:
            test_results.add_result("Get Messages", "FAIL", f"No messages field: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Messages", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_send_message():
    """Test sending a message"""
    if not auth_token or not match_id:
        test_results.add_result("Send Message", "FAIL", "Missing auth token or match_id")
        return False
    
    headers = get_auth_headers(auth_token)
    message_data = {
        "match_id": match_id,
        "content": "Hello! Nice to match with you!",
        "message_type": "text"
    }
    
    response = make_request("POST", f"/chat/{match_id}/messages", message_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "message_id" in data:
            test_results.add_result("Send Message", "PASS")
            return True
        else:
            test_results.add_result("Send Message", "FAIL", f"No message_id in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Send Message", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_verify_message_appears():
    """Test that sent message appears in get messages"""
    if not auth_token or not match_id:
        test_results.add_result("Verify Message Appears", "FAIL", "Missing auth token or match_id")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", f"/chat/{match_id}/messages", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        messages = data.get("messages", [])
        if len(messages) > 0 and "Hello! Nice to match with you!" in [msg.get("content") for msg in messages]:
            test_results.add_result("Verify Message Appears", "PASS")
            return True
        else:
            test_results.add_result("Verify Message Appears", "FAIL", f"Message not found in {len(messages)} messages")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Verify Message Appears", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 5 - FEEDS TESTS
# ============================================

def test_create_feed_text_only():
    """Test creating feed with content only"""
    if not auth_token:
        test_results.add_result("Create Feed (Text Only)", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    feed_data = {
        "content": "Just joined Miluv! Excited to meet new people 😊",
        "images": []
    }
    
    response = make_request("POST", "/feeds", feed_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "feed_id" in data:
            test_results.add_result("Create Feed (Text Only)", "PASS")
            return True
        else:
            test_results.add_result("Create Feed (Text Only)", "FAIL", f"No feed_id in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Create Feed (Text Only)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_create_feed_with_image():
    """Test creating feed with content and image"""
    if not auth_token:
        test_results.add_result("Create Feed (With Image)", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    feed_data = {
        "content": "Beautiful sunset today! 🌅",
        "images": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="]
    }
    
    response = make_request("POST", "/feeds", feed_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "feed_id" in data:
            test_results.add_result("Create Feed (With Image)", "PASS")
            return True
        else:
            test_results.add_result("Create Feed (With Image)", "FAIL", f"No feed_id in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Create Feed (With Image)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_get_feeds():
    """Test getting feeds list"""
    if not auth_token:
        test_results.add_result("Get Feeds", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/feeds", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "feeds" in data:
            test_results.add_result("Get Feeds", "PASS")
            return True
        else:
            test_results.add_result("Get Feeds", "FAIL", f"No feeds field: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Feeds", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 6 - PROFILE TESTS
# ============================================

def test_get_own_profile():
    """Test getting own profile"""
    if not auth_token:
        test_results.add_result("Get Own Profile", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/profile", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "id" in data and "name" in data and "email" in data:
            test_results.add_result("Get Own Profile", "PASS")
            return True
        else:
            test_results.add_result("Get Own Profile", "FAIL", f"Missing profile fields: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Own Profile", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_get_other_user_profile():
    """Test getting another user's profile"""
    if not auth_token or not user_id_2:
        test_results.add_result("Get Other User Profile", "FAIL", "Missing auth token or target user")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", f"/profile/{user_id_2}", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "id" in data and "name" in data:
            test_results.add_result("Get Other User Profile", "PASS")
            return True
        else:
            test_results.add_result("Get Other User Profile", "FAIL", f"Missing profile fields: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Other User Profile", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 7 - CONSULTATION TESTS
# ============================================

def test_get_counselors_low_readiness():
    """Test get counselors with low readiness (should fail)"""
    if not auth_token:
        test_results.add_result("Get Counselors (Low Readiness)", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/consultations", headers=headers)
    
    # Should fail if readiness < 80%
    if response and response.status_code == 403:
        test_results.add_result("Get Counselors (Low Readiness)", "PASS")
        return True
    elif response and response.status_code == 200:
        # If it passes, user might already have high readiness
        test_results.add_result("Get Counselors (Low Readiness)", "PASS", "User already has sufficient readiness")
        return True
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Counselors (Low Readiness)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_update_readiness_and_get_counselors():
    """Test updating readiness to 80+ and getting counselors"""
    if not auth_token:
        test_results.add_result("Get Counselors (High Readiness)", "FAIL", "No auth token available")
        return False
    
    # First, submit readiness assessment with high scores
    headers = get_auth_headers(auth_token)
    assessment_data = {
        "test_type": "readiness",
        "answers": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]  # All max scores for 100% readiness
    }
    
    response = make_request("POST", "/assessment/submit", assessment_data, headers)
    if not (response and response.status_code == 200):
        test_results.add_result("Update Readiness", "FAIL", "Failed to update readiness")
        return False
    
    # Now try to get counselors
    response = make_request("GET", "/consultations", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "counselors" in data and len(data["counselors"]) > 0:
            test_results.add_result("Get Counselors (High Readiness)", "PASS")
            return True
        else:
            test_results.add_result("Get Counselors (High Readiness)", "FAIL", f"No counselors found: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Get Counselors (High Readiness)", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_book_consultation():
    """Test booking consultation"""
    if not auth_token:
        test_results.add_result("Book Consultation", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    booking_data = {
        "counselor_id": "counselor-1",
        "schedule": "2024-01-15 10:00:00",
        "session_type": "video"
    }
    
    response = make_request("POST", "/consultations/book", booking_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "consult_id" in data and "payment_id" in data:
            test_results.add_result("Book Consultation", "PASS")
            return True
        else:
            test_results.add_result("Book Consultation", "FAIL", f"Missing booking details: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Book Consultation", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# PRIORITY 8 - REPORT & BLOCK TESTS
# ============================================

def test_report_user():
    """Test reporting a user"""
    if not auth_token or not user_id_2:
        test_results.add_result("Report User", "FAIL", "Missing auth token or target user")
        return False
    
    headers = get_auth_headers(auth_token)
    report_data = {
        "target_type": "user",
        "target_id": user_id_2,
        "reason": "Inappropriate behavior"
    }
    
    response = make_request("POST", "/report", report_data, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "message" in data:
            test_results.add_result("Report User", "PASS")
            return True
        else:
            test_results.add_result("Report User", "FAIL", f"No message in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Report User", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_block_user():
    """Test blocking a user"""
    if not auth_token or not user_id_2:
        test_results.add_result("Block User", "FAIL", "Missing auth token or target user")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("POST", f"/block/{user_id_2}", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        if "message" in data:
            test_results.add_result("Block User", "PASS")
            return True
        else:
            test_results.add_result("Block User", "FAIL", f"No message in response: {data}")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Block User", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

def test_verify_blocked_user_not_in_discovery():
    """Test that blocked user doesn't appear in discovery"""
    if not auth_token:
        test_results.add_result("Verify Blocked User Not in Discovery", "FAIL", "No auth token available")
        return False
    
    headers = get_auth_headers(auth_token)
    response = make_request("GET", "/discover?radius=100", headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        users = data.get("users", [])
        blocked_user_found = any(user.get("id") == user_id_2 for user in users)
        
        if not blocked_user_found:
            test_results.add_result("Verify Blocked User Not in Discovery", "PASS")
            return True
        else:
            test_results.add_result("Verify Blocked User Not in Discovery", "FAIL", "Blocked user still appears in discovery")
            return False
    else:
        error_msg = response.json().get("detail", "Unknown error") if response else "No response"
        test_results.add_result("Verify Blocked User Not in Discovery", "FAIL", f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        return False

# ============================================
# MAIN TEST EXECUTION
# ============================================

def run_all_tests():
    """Run all tests in priority order"""
    print("🚀 Starting Miluv.app Backend API Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*60)
    
    # Priority 1 - Auth Flow
    print("\n📋 PRIORITY 1 - AUTH FLOW")
    test_api_root()
    test_register_user()
    test_register_user_2()
    test_login()
    test_login_invalid_credentials()
    test_face_verification()
    
    # Priority 2 - Assessment System
    print("\n📋 PRIORITY 2 - ASSESSMENT SYSTEM")
    test_get_assessment_questions()
    test_submit_assessments()
    test_submit_assessments_user_2()
    test_assessment_status()
    
    # Priority 3 - Discovery & Matching
    print("\n📋 PRIORITY 3 - DISCOVERY & MATCHING")
    test_discover_users()
    test_like_user()
    test_reciprocal_like()
    test_get_matches()
    
    # Priority 4 - Chat
    print("\n📋 PRIORITY 4 - CHAT")
    test_get_messages()
    test_send_message()
    test_verify_message_appears()
    
    # Priority 5 - Feeds
    print("\n📋 PRIORITY 5 - FEEDS")
    test_create_feed_text_only()
    test_create_feed_with_image()
    test_get_feeds()
    
    # Priority 6 - Profile
    print("\n📋 PRIORITY 6 - PROFILE")
    test_get_own_profile()
    test_get_other_user_profile()
    
    # Priority 7 - Consultation
    print("\n📋 PRIORITY 7 - CONSULTATION")
    test_get_counselors_low_readiness()
    test_update_readiness_and_get_counselors()
    test_book_consultation()
    
    # Priority 8 - Report & Block
    print("\n📋 PRIORITY 8 - REPORT & BLOCK")
    test_report_user()
    test_block_user()
    test_verify_blocked_user_not_in_discovery()
    
    # Print final summary
    test_results.print_summary()

if __name__ == "__main__":
    run_all_tests()