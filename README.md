# Agentic Honey-Pot API for Scam Intelligence

## Executive Summary

The Agentic Honey-Pot is an advanced AI-driven security system designed to detect, engage, and analyze fraudulent communications. By simulating human responses, the system autonomously engages threat actors in multi-turn conversations to extract actionable intelligence—including financial identifiers and phishing infrastructure—without revealing its automated nature.

This solution is engineered to support the **Scam Detection & Intelligence Extraction** challenge, providing a robust, stateless REST API that integrates seamlessly with evaluation platforms.

## Core Capabilities

*   **Intelligent Scam Detection**: Real-time analysis of incoming messages using extensive keyword heuristics and pattern matching to identify financial fraud, urgency tactics, and verification scams.
*   **Autonomous Engagement Agent**: A dynamic, context-aware AI persona that adapts its responses (Initial Curiosity → Engagement → Data Extraction) to prolong interactions and elicit information.
*   **Strategic Intelligence Extraction**: Automatically parses conversation history to identify and log:
    *   Target Bank Accounts and IFSC Codes
    *   Fraudulent UPI IDs
    *   Scammer Phone Numbers
    *   Phishing URLs
*   **Stateless Architecture**: Fully RESTful design utilizing `conversationHistory` for context management, ensuring high scalability and reliability across distributed environments.
*   **Automated Reporting**: Integrated callback mechanism to the GUVI evaluation platform, ensuring real-time reporting of confirmed threats and extracted intelligence.

## Technical Specifications

*   **Runtime**: Python 3.11+
*   **Framework**: FastAPI (High-performance Async I/O)
*   **Server**: Uvicorn (ASGI)
*   **Deployment**: Ready for Render/Docker environments
*   **Authentication**: API Key enforcement (`x-api-key`)

## API Documentation

### Authentication

All requests to the API must be authenticated using the following header:

```http
x-api-key: scam_hunter_2026_secure_key
```

### Endpoints

#### 1. Analyze Message (`POST /api/analyze-message`)

The primary endpoint for processing incoming messages. It analyzes the content, updates the conversation state, and generates an appropriate agent response.

**Request Body Schema:**

```json
{
  "sessionId": "string (UUID)",
  "message": {
    "sender": "string (scammer|user)",
    "text": "string (message content)",
    "timestamp": "integer (epoch ms)"
  },
  "conversationHistory": [
    {
      "sender": "string",
      "text": "string",
      "timestamp": "integer"
    }
  ],
  "metadata": {
    "channel": "string (SMS|WhatsApp)",
    "language": "string",
    "locale": "string"
  }
}
```

**Response Schema:**

```json
{
  "status": "success",
  "reply": "string (Agent's response)"
}
```

#### 2. Health Check (`GET /health`)

Returns the operational status of the service. Useful for uptime monitoring and load balancers.

**Response:**
```json
{ "status": "healthy" }
```

## System Logic & Workflow

1.  **Ingestion**: The API receives a POST request with the latest message and full conversation history.
2.  **Detection**: The system scans the aggregate text for known scam vectors (e.g., "block", "verify", "prize").
3.  **Contextualization**: The AI Agent determines the conversation stage (Initial, Requesting Details, Engaged) based on the interaction history.
4.  **Response Generation**: A human-like response is generated to encourage the scammer to reveal more information.
5.  **Intelligence Reporting**: If a scam is confirmed and engagement has occurred, the system asynchronously sends a detailed report to the **GUVI Evaluation Callback Endpoint**, including all extracted entities and agent notes.

## Deployment & Setup

### Local Environment

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/aneeshsrinivas/honeypot-api.git
    cd honeypot-api
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch Server**:
    ```bash
    python -m uvicorn app:app --host 0.0.0.0 --port 8000
    ```

### Cloud Deployment (Render)

This repository is optimized for deployment on Render.com.
1.  Link your repository to Render.
2.  Select **Web Service**.
3.  Set Build Command: `pip install -r requirements.txt`
4.  Set Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

*Developed for the GUVI Agentic Honey-Pot Challenge.*
