import requests
import time
import uuid
import os
import logging
import secrets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_PASSWORD = secrets.token_urlsafe(16)

def run_tests():
    logger.info("Starting E2E Tests for Saga-lite Microservice Platform")
    
    username = f"user_{uuid.uuid4().hex[:6]}"
    logger.info(f"Test 1: User Registration for {username}")
    
    try:
        reg_res = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": TEST_PASSWORD,
            "role": "admin"
        }, timeout=5)
        reg_res.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to connect or register: {e}")
        return

    logger.info("Test 2: Authentication (JWT)")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": TEST_PASSWORD
    }, timeout=5)
    
    assert login_res.status_code == 200, "Authentication failed"
    access_token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    logger.info("JWT successfully acquired")

    logger.info("Test 3: Triggering Standard Workflow")
    orch_res = requests.post(f"{BASE_URL}/orchestrator/orchestrate", 
                             json={"user_input": "Setup my profile and notify me"},
                             headers=headers, timeout=5)
                             
    job_id = orch_res.json().get("job_id")
    logger.info(f"Orchestration job dispatched: {job_id}")

    success = False
    for _ in range(10):
        time.sleep(2)
        status_res = requests.get(f"{BASE_URL}/orchestrator/executions/{job_id}", headers=headers, timeout=5)
        status_data = status_res.json()
        logger.debug(f"Job Status: {status_data.get('status')}")
        if status_data.get('status') == "completed":
            logger.info("Standard Flow completed successfully")
            success = True
            break
            
    assert success, "Standard flow did not complete in time"

    logger.info("Test 4: Triggering Saga Compensation Flow")
    fail_username = f"user_fail_{uuid.uuid4().hex[:6]}"
    
    # Pre-register user to fail
    requests.post(f"{BASE_URL}/auth/register", json={
        "username": fail_username,
        "email": f"{fail_username}@example.com",
        "password": TEST_PASSWORD,
        "role": "admin"
    }, timeout=5)
    
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "username": fail_username,
        "password": TEST_PASSWORD
    }, timeout=5)
    
    fail_token = login_res.json().get("access_token")
    fail_headers = {"Authorization": f"Bearer {fail_token}"}

    orch_res = requests.post(f"{BASE_URL}/orchestrator/orchestrate", 
                             json={"user_input": f"Create user {fail_username}"},
                             headers=fail_headers, timeout=5)
    fail_job_id = orch_res.json().get("job_id")
    
    comp_success = False
    for _ in range(12):
        time.sleep(2)
        status_res = requests.get(f"{BASE_URL}/orchestrator/executions/{fail_job_id}", headers=headers, timeout=5)
        status_data = status_res.json()
        logger.debug(f"Job Status: {status_data.get('status')}")
        if status_data.get('status') == "compensated":
            logger.info("Compensation Logic correctly detected failure and rolled back")
            comp_success = True
            break
            
    assert comp_success, "Saga compensation did not finish properly"
    logger.info("All workflow tests passed successfully.")

if __name__ == "__main__":
    run_tests()
