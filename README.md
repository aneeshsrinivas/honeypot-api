# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

## Project Overview

The Agentic Honey-Pot is an AI-powered security system designed to detect scam attempts, engage malicious actors in multi-turn conversations, and extract actionable intelligence. This system operates as a REST API that analyzes incoming messages, determines if they exhibit fraudulent intent, and autonomously manages the interaction to gather critical data such as bank account details, UPI IDs, and phishing links without revealing its automated nature.

This solution addresses the growing sophistication of financial fraud by deploying an adaptive agent that wastes scammer resources while collecting evidence for security analysis.

## Core Features

- **Automated Scam Detection**: Utilizes keyword analysis and pattern matching to identify fraudulent messages related to banking, prizes, threats, and verification requests.
- **Autonomous AI Agent**: Engages scammers in natural, context-aware conversations to maintain engagement and elicit information.
- **Intelligence Extraction**: automatically parses messages to identify and log extracting entities including:
  - Bank Account Numbers
  - UPI IDs
  - Phone Numbers
  - Phishing URLs
  - IFSC Codes
- **Session Management**: Maintains conversation state across multiple turns to ensure coherent and logical responses.
- **Stealth Operation**: Designed to mimic human behavioral patterns (concern, excitement, confusion) to avoid detection by scammers.
- **GUVI Hackathon Integration**: Includes automated callback mechanisms to report detected scams and extracted intelligence to the evaluation platform.

## Technical Architecture

The system is built using a modern, lightweight, and scalable stack:

- **Framework**: FastAPI (Python) for high-performance asynchronous API handling.
- **Server**: Uvicorn as the ASGI web server implementation.
- **Runtime**: Python 3.11+
- **Deployment**: Configured for Render.com with automatic build and deployment pipelines.
- **Data Handling**: In-memory session storage for rapid processing and state management.

## Installation and Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git version control system

### Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/aneeshsrinivas/honeypot-api.git
   cd honeypot-api
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python -m uvicorn app:app --reload
   ```
   The API will be available at http://localhost:8000.

## API Documentation

### Authentication

All API requests must include the following header for authentication:

```
x-api-key: scam_hunter_2026_secure_key
```

### Analyze Message Endpoint

**URL**: `/api/analyze-message`
**Method**: `POST`
**Content-Type**: `application/json`

#### Request Format

The API accepts multiple request formats to ensure compatibility with various testing tools and real-world inputs.

**Standard Format:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Simplified Format:**
```json
{
  "message": "Your account will be blocked"
}
```

#### Response Format

```json
{
  "status": "success",
  "reply": "Oh no! I do not want my account blocked. What information do you need?"
}
```

### Health Check Endpoint

**URL**: `/health`
**Method**: `GET`

Returns the operational status of the service.

## Security & Compliance

- **Input Validation**: Robust parsing of incoming JSON payloads to prevent injection attacks and handling logical errors.
- **Error Handling**: Graceful error management ensures the system remains stable even when receiving malformed requests.
- **Data Privacy**: No personal data is permanently stored; session data exists only for the duration of the active conversation context.

## Deployment

This repository includes a `render.yaml` configuration file for seamless deployment on Render.

1. Connect your GitHub repository to Render.
2. Select "Blueprints" and choose this repository.
3. Render will automatically detect the configuration and deploy the service.

## Testing

You can test the API using cURL or Postman:

```bash
curl -X POST https://your-app-url.onrender.com/api/analyze-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: scam_hunter_2026_secure_key" \
  -d '{"message": "Your account will be blocked"}'
```

## License

This project is developed for the GUVI Agentic Honey-Pot Challenge. All rights reserved.
