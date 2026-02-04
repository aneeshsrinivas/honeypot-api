import requests
import uuid
import time

BASE_URL = "http://localhost:8000/api/analyze-message"
API_KEY = "scam_hunter_2026_secure_key"

def test_flow():
    session_id = str(uuid.uuid4())
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # 1. First Message
    print("\n--- Sending First Message ---")
    payload_1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }
    
    start = time.time()
    resp1 = requests.post(BASE_URL, json=payload_1, headers=headers)
    duration = time.time() - start
    print(f"Status: {resp1.status_code}, Time: {duration:.4f}s")
    print(f"Response: {resp1.json()}")
    
    if resp1.status_code != 200:
        print("FAILED Step 1")
        return

    # 2. Second Message (Follow-up)
    print("\n--- Sending Second Message ---")
    payload_2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Please share your UPI ID.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [
            payload_1["message"],
            {"sender": "user", "text": resp1.json().get("reply", "Huh?"), "timestamp": int(time.time() * 1000)}
        ],
        "metadata": {"channel": "SMS"}
    }
    
    start = time.time()
    resp2 = requests.post(BASE_URL, json=payload_2, headers=headers)
    duration = time.time() - start
    print(f"Status: {resp2.status_code}, Time: {duration:.4f}s")
    print(f"Response: {resp2.json()}")
    
    if resp2.status_code != 200:
        print("FAILED Step 2")
        return

    print("\nSUCCESS: All steps passed with valid responses.")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test failed: {e}")
