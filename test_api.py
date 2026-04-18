import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

test_results = {"passed": 0, "failed": 0}


def print_test(title, method, endpoint, status):
    """Print test result"""
    color = GREEN if status == "✓" else RED
    print(f"{color}{status}{RESET} {method.ljust(6)} {endpoint.ljust(30)} {title}")


def test_create_profile():
    """Test POST /api/profiles"""
    print(f"\n{BLUE}=== TEST: CREATE PROFILE ==={RESET}")
    
    # Test 1: Create first profile
    data = {"name": "ella"}
    response = requests.post(f"{BASE_URL}/api/profiles", json=data)
    
    if response.status_code == 201:
        result = response.json()
        if result["status"] == "success" and "id" in result["data"]:
            print_test("Create new profile (ella)", "POST", "/api/profiles", "✓")
            test_results["passed"] += 1
            profile_id = result["data"]["id"]
            return profile_id
        else:
            print_test("Create new profile - Invalid response format", "POST", "/api/profiles", "✗")
            test_results["failed"] += 1
            return None
    else:
        print_test(f"Create new profile - Status {response.status_code}", "POST", "/api/profiles", "✗")
        print(f"  Response: {response.text}")
        test_results["failed"] += 1
        return None


def test_duplicate_profile():
    """Test duplicate name handling"""
    print(f"\n{BLUE}=== TEST: DUPLICATE PROFILE HANDLING ==={RESET}")
    
    data = {"name": "ella"}
    response = requests.post(f"{BASE_URL}/api/profiles", json=data)
    
    if response.status_code == 201:
        result = response.json()
        if result["status"] == "success" and result.get("message") == "Profile already exists":
            print_test("Return existing profile on duplicate", "POST", "/api/profiles", "✓")
            test_results["passed"] += 1
        else:
            print_test("Duplicate handling - Wrong response", "POST", "/api/profiles", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"Duplicate handling - Status {response.status_code}", "POST", "/api/profiles", "✗")
        test_results["failed"] += 1


def test_get_single_profile(profile_id):
    """Test GET /api/profiles/{id}"""
    print(f"\n{BLUE}=== TEST: GET SINGLE PROFILE ==={RESET}")
    
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
    
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success" and result["data"]["id"] == profile_id:
            print_test(f"Get profile by ID", "GET", f"/api/profiles/{profile_id}", "✓")
            test_results["passed"] += 1
        else:
            print_test("Get single profile - Invalid response", "GET", f"/api/profiles/{profile_id}", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"Get single profile - Status {response.status_code}", "GET", f"/api/profiles/{profile_id}", "✗")
        test_results["failed"] += 1


def test_get_all_profiles():
    """Test GET /api/profiles"""
    print(f"\n{BLUE}=== TEST: LIST ALL PROFILES ==={RESET}")
    
    response = requests.get(f"{BASE_URL}/api/profiles")
    
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success" and "count" in result:
            print_test(f"List all profiles (count: {result['count']})", "GET", "/api/profiles", "✓")
            test_results["passed"] += 1
        else:
            print_test("List all profiles - Invalid response", "GET", "/api/profiles", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"List all profiles - Status {response.status_code}", "GET", "/api/profiles", "✗")
        test_results["failed"] += 1


def test_filtering():
    """Test filtering with query parameters"""
    print(f"\n{BLUE}=== TEST: FILTERING ==={RESET}")
    
    # Create a few more profiles first
    names = ["john", "sarah", "ahmed"]
    for name in names:
        requests.post(f"{BASE_URL}/api/profiles", json={"name": name})
    
    # Test gender filter (case-insensitive)
    response = requests.get(f"{BASE_URL}/api/profiles?gender=female")
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            print_test(f"Filter by gender (female) - count: {result['count']}", "GET", "/api/profiles?gender=female", "✓")
            test_results["passed"] += 1
        else:
            print_test("Filter by gender - Invalid response", "GET", "/api/profiles?gender=female", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"Filter by gender - Status {response.status_code}", "GET", "/api/profiles?gender=female", "✗")
        test_results["failed"] += 1
    
    # Test multiple filters
    response = requests.get(f"{BASE_URL}/api/profiles?gender=male&age_group=adult")
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            print_test(f"Filter by multiple params", "GET", "/api/profiles?gender=male&age_group=adult", "✓")
            test_results["passed"] += 1
        else:
            print_test("Multiple filters - Invalid response", "GET", "/api/profiles?...", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"Multiple filters - Status {response.status_code}", "GET", "/api/profiles?...", "✗")
        test_results["failed"] += 1


def test_delete_profile():
    """Test DELETE /api/profiles/{id}"""
    print(f"\n{BLUE}=== TEST: DELETE PROFILE ==={RESET}")
    
    # Create a profile to delete
    data = {"name": "tobedeleted"}
    response = requests.post(f"{BASE_URL}/api/profiles", json=data)
    
    if response.status_code == 201:
        profile_id = response.json()["data"]["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/profiles/{profile_id}")
        
        if response.status_code == 204:
            print_test(f"Delete profile", "DELETE", f"/api/profiles/{profile_id}", "✓")
            test_results["passed"] += 1
            
            # Verify it's gone
            response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}")
            if response.status_code == 404:
                print_test(f"Verify deleted profile returns 404", "GET", f"/api/profiles/{profile_id}", "✓")
                test_results["passed"] += 1
            else:
                print_test("Verify deletion - Should return 404", "GET", f"/api/profiles/{profile_id}", "✗")
                test_results["failed"] += 1
        else:
            print_test(f"Delete profile - Status {response.status_code}", "DELETE", f"/api/profiles/{profile_id}", "✗")
            test_results["failed"] += 1
    else:
        print_test("Delete profile - Failed to create test profile", "DELETE", "/api/profiles/...", "✗")
        test_results["failed"] += 1


def test_error_cases():
    """Test error scenarios"""
    print(f"\n{BLUE}=== TEST: ERROR HANDLING ==={RESET}")
    
    # Test 1: Empty name
    response = requests.post(f"{BASE_URL}/api/profiles", json={"name": ""})
    if response.status_code == 400:
        result = response.json()
        if result["status"] == "error":
            print_test("Empty name returns 400", "POST", "/api/profiles", "✓")
            test_results["passed"] += 1
        else:
            print_test("Empty name - Invalid error format", "POST", "/api/profiles", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"Empty name - Wrong status {response.status_code}", "POST", "/api/profiles", "✗")
        test_results["failed"] += 1
    
    # Test 2: Non-existent ID
    response = requests.get(f"{BASE_URL}/api/profiles/nonexistent-id")
    if response.status_code == 404:
        result = response.json()
        if result["status"] == "error":
            print_test("Non-existent ID returns 404", "GET", "/api/profiles/...", "✓")
            test_results["passed"] += 1
        else:
            print_test("404 - Invalid error format", "GET", "/api/profiles/...", "✗")
            test_results["failed"] += 1
    else:
        print_test(f"404 - Wrong status {response.status_code}", "GET", "/api/profiles/...", "✗")
        test_results["failed"] += 1


def test_health_check():
    """Test health check endpoint"""
    print(f"\n{BLUE}=== TEST: HEALTH CHECK ==={RESET}")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print_test("Health check", "GET", "/health", "✓")
        test_results["passed"] += 1
    else:
        print_test(f"Health check - Status {response.status_code}", "GET", "/health", "✗")
        test_results["failed"] += 1


def test_cors_headers():
    """Test CORS headers"""
    print(f"\n{BLUE}=== TEST: CORS HEADERS ==={RESET}")
    
    response = requests.get(f"{BASE_URL}/health")
    cors_header = response.headers.get("Access-Control-Allow-Origin")
    
    if cors_header == "*":
        print_test("CORS header present", "GET", "/health", "✓")
        test_results["passed"] += 1
    else:
        print_test(f"CORS header missing or wrong: {cors_header}", "GET", "/health", "✗")
        test_results["failed"] += 1


def run_all_tests():
    """Run all tests"""
    print(f"\n{YELLOW}{'='*60}")
    print(f"BACKEND WIZARDS STAGE 1 - API TEST SUITE")
    print(f"{'='*60}{RESET}")
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"\n{RED}ERROR: Server not running at {BASE_URL}{RESET}")
        print(f"Start the server with: {YELLOW}uvicorn main:app --reload{RESET}")
        return
    
    print(f"\n{GREEN}✓ Server is running{RESET}\n")
    
    # Run tests
    test_health_check()
    test_cors_headers()
    
    profile_id = test_create_profile()
    if profile_id:
        test_duplicate_profile()
        test_get_single_profile(profile_id)
    
    test_get_all_profiles()
    test_filtering()
    test_delete_profile()
    test_error_cases()
    
    # Summary
    print(f"\n{YELLOW}{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}{RESET}")
    print(f"{GREEN}Passed: {test_results['passed']}{RESET}")
    print(f"{RED}Failed: {test_results['failed']}{RESET}")
    
    total = test_results['passed'] + test_results['failed']
    percentage = (test_results['passed'] / total * 100) if total > 0 else 0
    
    color = GREEN if percentage >= 80 else YELLOW if percentage >= 60 else RED
    print(f"{color}Success Rate: {percentage:.1f}%{RESET}\n")


if __name__ == "__main__":
    run_all_tests()
