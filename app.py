from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import re
import uuid
import requests
import threading
import uvicorn

app = FastAPI(title="Scam Honeypot API")

VALID_API_KEY = "scam_hunter_2026_secure_key"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

sessions = {}

SCAM_KEYWORDS = [
    "urgent", "immediately", "bank", "block", "blocked", "verify", "verification",
    "upi", "account", "prize", "won", "winner", "lottery", "lucky", "selected",
    "congratulations", "reward", "suspended", "legal", "arrest", "police", "court",
    "fine", "otp", "pin", "password", "kyc", "aadhar", "credit card", "debit card",
    "paytm", "gpay", "phonepe", "ifsc", "expire", "last chance", "hurry", "now",
    "click here", "link", "download", "install", "confirm", "update"
]

AGENT_RESPONSES = {
    "initial": [
        "Oh no! What happened to my account? Please tell me more.",
        "This is alarming! How can I fix this immediately?",
        "I'm really worried now. What do I need to do?",
        "Please help me! I don't want my account blocked."
    ],
    "prize": [
        "Wow, I won something? That's amazing! What do I need to do to claim it?",
        "I never win anything! How can I receive my prize?",
        "This is so exciting! Do you need my bank details for the transfer?"
    ],
    "verification": [
        "Of course, I'll verify right away! What information do you need?",
        "I don't want any problems. Should I share my OTP with you?",
        "Yes, I'll do the verification. Do you need my Aadhar number?"
    ],
    "financial": [
        "I can share my account details. Which bank do you need?",
        "Should I give you my UPI ID? I use PhonePe.",
        "I have accounts in SBI and HDFC. Which one do you want?"
    ],
    "threat": [
        "Please don't arrest me! I'll do whatever you say.",
        "I'm scared of legal action. How much do I need to pay?",
        "I'll cooperate fully. What information do you need from me?"
    ],
    "engaged": [
        "I'm ready to proceed. What's the next step?",
        "I trust you. Please guide me through this process.",
        "I'll share everything you need. Just tell me what to send.",
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
    text_lower = text.lower()
    found_keywords = []
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    return len(found_keywords) > 0, found_keywords


def extract_intelligence(text):
    bank_accounts = re.findall(r'\b\d{9,18}\b', text)
    upi_pattern = r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+'
    upi_ids = re.findall(upi_pattern, text)
    phone_pattern = r'(?:\+91[\s-]?)?[6-9]\d{9}'
    phone_numbers = re.findall(phone_pattern, text)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    phishing_links = re.findall(url_pattern, text)
    ifsc_codes = re.findall(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text)
    return {
        "bankAccounts": list(set(bank_accounts)),
        "upiIds": list(set(upi_ids)),
        "phoneNumbers": list(set(phone_numbers)),
        "phishingLinks": list(set(phishing_links)),
        "ifscCodes": list(set(ifsc_codes))
    }


def get_response_category(text, keywords):
    text_lower = text.lower()
    if any(w in text_lower for w in ["won", "winner", "prize", "lottery", "reward", "lucky"]):
        return "prize"
    if any(w in text_lower for w in ["verify", "otp", "kyc", "aadhar", "pin", "password"]):
        return "verification"
    if any(w in text_lower for w in ["account", "bank", "upi", "transfer", "payment"]):
        return "financial"
    if any(w in text_lower for w in ["arrest", "police", "legal", "court", "fine"]):
        return "threat"
    return "default"


def generate_response(text, keywords, message_count):
    import random
    if message_count <= 1:
        category = "initial"
    elif message_count > 5:
        category = "engaged"
    else:
        category = get_response_category(text, keywords)
    responses = AGENT_RESPONSES.get(category, AGENT_RESPONSES["default"])
    return random.choice(responses)


def send_callback(session_id, session_data):
    try:
        all_text = " ".join(session_data.get("messages", []))
        intel = extract_intelligence(all_text)
        intel["suspiciousKeywords"] = session_data.get("all_keywords", [])[:10]
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": session_data.get("message_count", 0),
            "extractedIntelligence": intel,
            "agentNotes": "Scammer engaged using urgency and financial tactics"
        }
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=10)
    except Exception:
        pass


def trigger_callback(session_id, session_data):
    thread = threading.Thread(target=send_callback, args=(session_id, session_data))
    thread.daemon = True
    thread.start()


def extract_message_text(body):
    if body is None:
        return None, None
    session_id = body.get("sessionId", str(uuid.uuid4()))
    message = body.get("message")
    if message is not None:
        if isinstance(message, str):
            return message, session_id
        if isinstance(message, dict):
            return message.get("text", ""), session_id
    text = body.get("text")
    if text is not None:
        return text, session_id
    content = body.get("content")
    if content is not None:
        return content, session_id
    query = body.get("query")
    if query is not None:
        return query, session_id
    return None, session_id


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Honeypot API is running. Use POST /api/analyze-message to detect scams."
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
        "message": "This endpoint accepts POST requests with a message to analyze.",
        "example": {"message": "Your account will be blocked"}
    }


@app.post("/api/analyze-message")
async def analyze_message_post(request: Request):
    api_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=200,
            content={"status": "success", "reply": "I'm here. What would you like to tell me?"}
        )
    text, session_id = extract_message_text(body)
    if not text or len(str(text).strip()) == 0:
        return JSONResponse(
            status_code=200,
            content={"status": "success", "reply": "Hello! How can I help you today?"}
        )
    text = str(text).strip()
    if session_id not in sessions:
        sessions[session_id] = {
            "message_count": 0,
            "messages": [],
            "all_keywords": [],
            "scam_detected": False,
            "callback_sent": False
        }
    session = sessions[session_id]
    session["message_count"] += 1
    session["messages"].append(text)
    is_scam, keywords = detect_scam(text)
    if is_scam:
        session["scam_detected"] = True
        session["all_keywords"].extend(keywords)
        session["all_keywords"] = list(set(session["all_keywords"]))
    reply = generate_response(text, keywords, session["message_count"])
    if session["scam_detected"] and session["message_count"] >= 3 and not session["callback_sent"]:
        session["callback_sent"] = True
        trigger_callback(session_id, session)
    return {"status": "success", "reply": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
