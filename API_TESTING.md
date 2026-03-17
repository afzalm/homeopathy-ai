# 🧪 API Testing Guide

Complete guide to testing the Homeopathy AI API.

---

## 🌐 Interactive Testing (Easiest)

### Step 1: Start the Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Open API Docs
Go to: **http://localhost:8000/docs**

### Step 3: Test Endpoints
1. Click on an endpoint
2. Click **Try it out**
3. Fill in parameters
4. Click **Execute**

---

## 📝 Testing Workflow

### 1. Create a Session
**Endpoint**: `POST /api/v1/sessions`

**Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "stage": "initial",
  "created_at": "2026-03-17T01:50:00",
  "updated_at": "2026-03-17T01:50:00"
}
```

**Copy the `id`** — you'll need it for the next steps.

---

### 2. Send a Message
**Endpoint**: `POST /api/v1/chat/{session_id}/message`

**Replace `{session_id}`** with the ID from step 1.

**Request**:
```json
{
  "message": "I have a severe headache that started this morning"
}
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "reply": "Thank you for sharing that. Could you tell me more about the headache?",
  "stage": "symptom_collection",
  "symptoms_extracted": [
    {
      "text": "severe headache",
      "rubric_id": 123,
      "rubric_path": "Head > Pain > Severe",
      "confidence": 0.95
    }
  ],
  "analysis_ready": false,
  "message_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

---

### 3. Continue the Conversation
Send more messages to collect symptoms:

**Message 1**:
```json
{
  "message": "It's throbbing and worse with light"
}
```

**Message 2**:
```json
{
  "message": "I feel anxious and irritable"
}
```

**Message 3**:
```json
{
  "message": "It's worse in the morning and better after rest"
}
```

---

### 4. Trigger Analysis
**Endpoint**: `POST /api/v1/chat/{session_id}/analyse`

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "top_remedies": [
    {
      "remedy": "Belladonna",
      "repertory_score": 0.85,
      "rag_score": 0.78,
      "outcome_prior": 0.82,
      "final_score": 0.82,
      "matching_rubrics": [
        "Head > Pain > Throbbing",
        "Head > Pain > Worse light",
        "Mind > Anxiety"
      ]
    },
    {
      "remedy": "Bryonia",
      "repertory_score": 0.72,
      "rag_score": 0.68,
      "outcome_prior": 0.70,
      "final_score": 0.70,
      "matching_rubrics": [
        "Head > Pain > Worse motion",
        "Mind > Irritability"
      ]
    }
  ],
  "materia_medica": [
    {
      "remedy": "Belladonna",
      "text": "Belladonna is indicated for acute conditions with sudden onset...",
      "source": "Materia Medica",
      "confidence": 0.92
    }
  ],
  "explanation": "Based on the symptoms collected, Belladonna appears to be the best match...",
  "rubrics_used": [
    "Head > Pain > Throbbing",
    "Head > Pain > Worse light",
    "Mind > Anxiety"
  ],
  "generated_at": "2026-03-17T01:55:00"
}
```

---

### 5. Get Session State
**Endpoint**: `GET /api/v1/sessions/{session_id}/state`

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "stage": "analysis",
  "location": ["head"],
  "sensations": ["throbbing"],
  "modalities": ["worse with light", "better after rest"],
  "mental_symptoms": ["anxiety", "irritability"],
  "generals": [],
  "rubrics": [
    "Head > Pain > Throbbing",
    "Head > Pain > Worse light",
    "Mind > Anxiety"
  ],
  "missing_dimensions": ["generals"],
  "last_updated": "2026-03-17T01:55:00"
}
```

---

### 6. Get Conversation History
**Endpoint**: `GET /api/v1/chat/{session_id}/history`

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "role": "user",
    "content": "I have a severe headache that started this morning",
    "created_at": "2026-03-17T01:50:00"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "role": "assistant",
    "content": "Thank you for sharing that. Could you tell me more about the headache?",
    "created_at": "2026-03-17T01:50:05"
  }
]
```

---

## 🧪 Using cURL

### Create Session
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/chat/550e8400-e29b-41d4-a716-446655440001/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'
```

### Trigger Analysis
```bash
curl -X POST http://localhost:8000/api/v1/chat/550e8400-e29b-41d4-a716-446655440001/analyse
```

### Get Session State
```bash
curl -X GET http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440001/state
```

### Get History
```bash
curl -X GET http://localhost:8000/api/v1/chat/550e8400-e29b-41d4-a716-446655440001/history
```

---

## 🐍 Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Create session
response = requests.post(
    f"{BASE_URL}/sessions",
    json={"user_id": "550e8400-e29b-41d4-a716-446655440000"}
)
session = response.json()
session_id = session["id"]
print(f"Created session: {session_id}")

# Send message
response = requests.post(
    f"{BASE_URL}/chat/{session_id}/message",
    json={"message": "I have a severe headache"}
)
chat = response.json()
print(f"AI Response: {chat['reply']}")

# Trigger analysis
response = requests.post(
    f"{BASE_URL}/chat/{session_id}/analyse"
)
analysis = response.json()
print(f"Top remedy: {analysis['top_remedies'][0]['remedy']}")
print(f"Score: {analysis['top_remedies'][0]['final_score']}")
```

---

## 📊 Testing Scenarios

### Scenario 1: Acute Headache
```
Message 1: "I have a sudden severe headache"
Message 2: "It's throbbing and worse with light"
Message 3: "I feel anxious"
Message 4: "It started suddenly this morning"
```

### Scenario 2: Chronic Pain
```
Message 1: "I have chronic back pain"
Message 2: "It's a dull ache"
Message 3: "It's worse when I move"
Message 4: "I feel depressed about it"
```

### Scenario 3: Digestive Issues
```
Message 1: "I have stomach pain"
Message 2: "It's cramping"
Message 3: "It's worse after eating"
Message 4: "I feel bloated"
```

---

## ✅ Verification Checklist

- ✅ Server starts without errors
- ✅ API docs available at http://localhost:8000/docs
- ✅ Health check returns 200: http://localhost:8000/health
- ✅ Can create a session
- ✅ Can send messages
- ✅ Can get session state
- ✅ Can trigger analysis
- ✅ Can get conversation history
- ✅ Remedies are returned with scores
- ✅ Explanations are generated

---

## 🆘 Troubleshooting

### "Connection refused"
→ Server not running. Start with: `python -m uvicorn main:app --reload`

### "404 Not Found"
→ Wrong endpoint or session ID. Check the URL.

### "422 Unprocessable Entity"
→ Invalid request body. Check the JSON format.

### "500 Internal Server Error"
→ Server error. Check the console for error messages.

---

## 📚 API Documentation

For complete API documentation, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 💡 Tips

- Use the interactive docs for easy testing
- Copy session IDs from responses
- Test with different symptoms
- Check the console for debug messages
- Use `DEBUG=true` in `.env` for more logging

---

**Happy testing! 🧪**
