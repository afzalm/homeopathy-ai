# 🏥 Homeopathy AI Decision Support System

An AI-powered FastAPI application for homeopathic case analysis and remedy recommendation using Neo4j repertory graphs, vector-based Materia Medica retrieval, and LLM-driven case-taking.

## 🚀 Quick Start

### Windows
```bash
run.bat
```

### Mac/Linux
```bash
chmod +x run.sh
./run.sh
```

Then open http://localhost:8000/docs in your browser.

**See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.**

---

## 📋 Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+**
- **Neo4j 4.4+**
- **Redis 6+**

### Option 1: Install Locally
Download and install each service from their official websites.

### Option 2: Use Docker (Recommended)
```bash
docker-compose up -d
```

This starts PostgreSQL, Neo4j, and Redis automatically.

---

## 📁 Project Structure

```
homeopathy_api/
├── main.py                    ← FastAPI app entry point
├── requirements.txt           ← Python dependencies
├── .env                       ← Configuration (auto-created)
├── run.bat / run.sh          ← Startup scripts
├── docker-compose.yml        ← Docker services
│
├── core/
│   ├── config.py             ← Settings from environment
│   └── database.py           ← Async SQLAlchemy setup
│
├── database/
│   └── models.py             ← ORM models (Sessions, Messages, Symptoms, etc.)
│
├── models/
│   └── schemas.py            ← Pydantic request/response schemas
│
├── api/
│   ├── session_routes.py     ← Session management endpoints
│   ├── chat_routes.py        ← Conversation & analysis endpoints
│   ├── remedy_routes.py      ← Remedy lookup endpoints
│   └── case_routes.py        ← Case recording endpoints
│
├── services/
│   ├── session_manager.py    ← Core orchestration logic
│   ├── symptom_extractor.py  ← LLM-based symptom extraction
│   ├── repertory_engine.py   ← Neo4j rubric scoring
│   ├── rag_service.py        ← Vector-based Materia Medica retrieval
│   └── remedy_ranker.py      ← Weighted remedy ranking (50/30/20)
│
└── llm/
    └── case_agent.py         ← LLM conversation & explanation generation
```

---

## 🔌 API Endpoints

### Sessions
- `POST /api/v1/sessions` — Create a new consultation session
- `GET /api/v1/sessions/{id}` — Get session details
- `GET /api/v1/sessions/{id}/state` — Get full session state

### Chat
- `POST /api/v1/chat/{session_id}/message` — Send message, get AI response
- `POST /api/v1/chat/{session_id}/analyse` — Trigger remedy analysis
- `GET /api/v1/chat/{session_id}/history` — Get conversation history

### Remedies
- `GET /api/v1/remedies` — List all remedies
- `GET /api/v1/remedies/{id}` — Get remedy details

### Cases
- `POST /api/v1/cases` — Record a clinical case
- `GET /api/v1/cases/{id}` — Get case details
- `POST /api/v1/cases/{id}/remedy` — Add remedy to case
- `PUT /api/v1/cases/{id}/outcome` — Record treatment outcome

---

## 🔧 Configuration

Edit `.env` to customize:

```env
# App
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/homeopathy_ai

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379

# LLM (Anthropic, OpenAI, etc.)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key

# Ranking weights
WEIGHT_REPERTORY=0.50
WEIGHT_RAG=0.30
WEIGHT_OUTCOME=0.20
```

---

## 📖 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

---

## 🧪 Testing

### Using cURL
```bash
# Create session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "550e8400-e29b-41d4-a716-446655440000"}'

# Send message
curl -X POST http://localhost:8000/api/v1/chat/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a severe headache"}'

# Trigger analysis
curl -X POST http://localhost:8000/api/v1/chat/{session_id}/analyse
```

### Using the Interactive Docs
1. Open http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

---

## 🐛 Troubleshooting

### "Connection refused" (PostgreSQL)
```bash
# Check if running
psql -U postgres

# Or start with Docker
docker-compose up -d postgres
```

### "Connection refused" (Neo4j)
```bash
# Check if running
curl http://localhost:7474

# Or start with Docker
docker-compose up -d neo4j
```

### "Connection refused" (Redis)
```bash
# Check if running
redis-cli ping

# Or start with Docker
docker-compose up -d redis
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Port 8000 already in use
Edit `run.bat` or `run.sh` and change `--port 8000` to `--port 8001`

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — Get started in 5 minutes
- **[SETUP.md](SETUP.md)** — Detailed setup instructions
- **API Docs** — http://localhost:8000/docs (when running)

---

## 🏗️ Architecture

### Data Flow
1. **User sends message** → Session stored in PostgreSQL
2. **Symptom extraction** → LLM extracts structured symptoms
3. **Rubric mapping** → Symptoms mapped to homeopathic rubrics
4. **Repertory scoring** → Neo4j graph scores remedies
5. **RAG retrieval** → Vector DB retrieves Materia Medica excerpts
6. **Ranking** → Weighted combination (50% repertory, 30% RAG, 20% outcomes)
7. **Explanation** → LLM generates clinical explanation
8. **Response** → Top remedies with reasoning returned to user

### Key Services
- **SessionManager** — Orchestrates session lifecycle and state
- **SymptomExtractor** — LLM-based structured extraction
- **RepertoryEngine** — Neo4j-based rubric scoring
- **MateriaMedicaRAG** — Vector-based remedy information retrieval
- **RemedyRanker** — Weighted multi-factor ranking
- **CaseAgent** — LLM conversation and explanation generation

---

## 🔐 Security

- All database connections use async SQLAlchemy
- CORS middleware configured for frontend integration
- Environment variables for sensitive data
- Input validation via Pydantic schemas
- SQL injection protection via parameterized queries

---

## 📝 License

[Add your license here]

---

## 🤝 Contributing

[Add contribution guidelines here]

---

## 📞 Support

For issues or questions:
1. Check the [QUICKSTART.md](QUICKSTART.md)
2. Review the API docs at http://localhost:8000/docs
3. Check the code comments in each module

---

**Happy case-taking! 🏥**
