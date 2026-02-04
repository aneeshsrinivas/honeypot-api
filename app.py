from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import re
import uuid
import requests
import threading
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scam Honeypot API")

VALID_API_KEY = "scam_hunter_2026_secure_key"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

SCAM_KEYWORDS = [
    "urgent", "immediately", "bank", "block", "blocked", "verify", "verification",
    "upi", "account", "prize", "won", "winner", "lottery", "lucky", "selected",
    "congratulations", "reward", "suspended", "legal", "arrest", "police", "court",
    "fine", "otp", "pin", "password", "kyc", "aadhar", "credit card", "debit card",
    "paytm", "gpay", "phonepe", "ifsc", "expire", "last chance", "hurry", "now",
    "click here", "link", "download", "install", "confirm", "update", "suspension",
    "activity", "compromised", "fraud"
]

AGENT_RESPONSES = {
    "initial": [
        "Oh no! What happened to my account? Please tell me more.",
        "This is alarming! How can I fix this immediately?",
        "I am really worried now. What do I need to do?",
        "Please help me! I do not want my account blocked."
    ],
    "prize": [
        "Wow, I won something? That is amazing! What do I need to do to claim it?",
        "I never win anything! How can I receive my prize?",
        "This is so exciting! Do you need my bank details for the transfer?"
    ],
    "verification": [
        "Of course, I will verify right away! What information do you need?",
        "I do not want any problems. Should I share my OTP with you?",
        "Yes, I will do the verification. Do you need my Aadhar number?"
    ],
    "financial": [
        "I can share my account details. Which bank do you need?",
        "Should I give you my UPI ID? I use PhonePe.",
        "I have accounts in SBI and HDFC. Which one do you want?"
    ],
    "threat": [
        "Please do not arrest me! I will do whatever you say.",
        "I am scared of legal action. How much do I need to pay?",
        "I will cooperate fully. What information do you need from me?"
    ],
    "engaged": [
        "I am ready to proceed. What is the next step?",
        "I trust you. Please guide me through this process.",
        "I will share everything you need. Just tell me what to send.",
        "Should I transfer the money now? How much exactly?"
    ],
    "default": [
        "I see. Can you explain more about this?",
        "This sounds important. What should I do next?",
        "I want to resolve this. Please tell me more.",
        "How can I help you with this matter?"
    ]
}


def detect_scam(text):
    if not text:
        return False, []
    text_lower = str(text).lower()
    found_keywords = []
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    return len(found_keywords) > 0, found_keywords


def extract_intelligence(text):
    if not text:
        return {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
    text = str(text)
    bank_accounts = re.findall(r'\b\d{9,18}\b', text)
    upi_pattern = r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+'
    upi_ids = re.findall(upi_pattern, text)
    phone_pattern = r'(?:\+91[\s-]?)?[6-9]\d{9}'
    phone_numbers = re.findall(phone_pattern, text)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    phishing_links = re.findall(url_pattern, text)
    return {
        "bankAccounts": list(set(bank_accounts)),
        "upiIds": list(set(upi_ids)),
        "phoneNumbers": list(set(phone_numbers)),
        "phishingLinks": list(set(phishing_links)),
        "suspiciousKeywords": []
    }


def get_response_category(text):
    text_lower = str(text).lower()
    if any(w in text_lower for w in ["won", "winner", "prize", "lottery", "reward", "lucky"]):
        return "prize"
    if any(w in text_lower for w in ["verify", "otp", "kyc", "aadhar", "pin", "password"]):
        return "verification"
    if any(w in text_lower for w in ["account", "bank", "upi", "transfer", "payment"]):
        return "financial"
    if any(w in text_lower for w in ["arrest", "police", "legal", "court", "fine"]):
        return "threat"
    return "default"


def generate_response(text, message_count):
    import random
    if message_count <= 1:
        category = "initial"
    elif message_count > 5:
        category = "engaged"
    else:
        category = get_response_category(text)
    responses = AGENT_RESPONSES.get(category, AGENT_RESPONSES["default"])
    return random.choice(responses)


def send_callback(session_id, full_text, message_count, all_keywords):
    try:
        # Simulate small delay to ensure we are truly async and don't block
        time.sleep(0.1)
        intel = extract_intelligence(full_text)
        intel["suspiciousKeywords"] = list(set(all_keywords))[:15]
        
        # Dynamic Agent Notes based on what we found
        notes = "Scam detected."
        intel_found = False
        if intel["bankAccounts"]:
            notes += " Collected bank account details."
            intel_found = True
        if intel["upiIds"]:
            notes += " Collected UPI ID."
            intel_found = True
        if intel["phoneNumbers"]:
            notes += " Collected phone number."
            intel_found = True
        if intel["phishingLinks"]:
            notes += " Identified phishing link."
            intel_found = True
        
        if not intel_found:
             notes += " Engaging to extract details. Keywords found: " + ", ".join(intel["suspiciousKeywords"][:5])

        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": message_count,
            "extractedIntelligence": intel,
            "agentNotes": notes
        }
        logger.info(f"Sending callback for session {session_id}...")
        response = requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        logger.info(f"Callback response: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Callback error: {e}")


def trigger_callback(session_id, full_text, message_count, all_keywords):
    thread = threading.Thread(target=send_callback, args=(session_id, full_text, message_count, all_keywords))
    thread.daemon = True
    thread.start()


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Honeypot API is running."
    }


@app.head("/")
async def head_root():
    return JSONResponse(content={"status": "success"}, status_code=200)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/analyze-message")
async def analyze_message_get():
    return {
        "status": "success",
        "message": "Use POST /api/analyze-message"
    }


@app.post("/api/analyze-message")
async def analyze_message_post(request: Request):
    # 1. API Key Validation
    api_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if not api_key or api_key != VALID_API_KEY:
        return JSONResponse(
            status_code=401,
            content={"status": "error", "reply": "Invalid or missing API key"}
        )

    # 2. Parse Body safely
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "reply": "Invalid JSON"}
        )

    # 3. Extract Session & Message Info
    session_id = body.get("sessionId") or body.get("session_id") or str(uuid.uuid4())
    
    # Handle 'message' field which might be a dict or string per spec
    raw_message = body.get("message")
    current_text = ""
    if isinstance(raw_message, dict):
        current_text = raw_message.get("text", "")
    elif isinstance(raw_message, str):
        current_text = raw_message
    
    current_text = str(current_text).strip()
    
    # 4. Handle Conversation History (Stateless)
    conversation_history = body.get("conversationHistory", [])
    if not isinstance(conversation_history, list):
        conversation_history = []
    
    # Calculate total messages including current one
    message_count = len(conversation_history) + 1

    # 5. Detect Scam & Aggregate Intelligence
    # We analyze the current message for immediate response trigger
    is_scam, current_keywords = detect_scam(current_text)
    
    # We also reconstruct full conversation text for intelligence extraction
    full_conversation_text = current_text
    all_keywords = current_keywords.copy()
    
    for prev_msg in conversation_history:
        if isinstance(prev_msg, dict):
            p_text = prev_msg.get("text", "")
            full_conversation_text += " " + str(p_text)
            _, kws = detect_scam(p_text)
            all_keywords.extend(kws)
    
    # 6. Generate Reply
    reply = generate_response(current_text, message_count)

    # 7. Trigger Callback if criteria met
    # Criteria: Scam detected anywhere in history OR current message, AND we are deep enough in convo
    scam_detected_overall = len(all_keywords) > 0
    
    # Only callback if we have exchanged a few messages to gather intel, 
    # OR if it's clearly a scam and we want to report early. 
    # WE SEND CALLBACK ON EVERY TURN if Scam Detected to ensure "Final Result" is up to date.
    if scam_detected_overall and message_count >= 2:
         trigger_callback(session_id, full_conversation_text, message_count, all_keywords)

    return {
        "status": "success",
        "reply": reply
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
