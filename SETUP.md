# Homeopathy AI - Setup & Run Guide

## Prerequisites

You need to have these installed on your system:
- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **PostgreSQL** — [Download](https://www.postgresql.org/download/)
- **Neo4j** — [Download](https://neo4j.com/download/)
- **Redis** — [Download](https://redis.io/download) (or use Docker)

## Quick Start (Development)

### 1. Install Python Dependencies

```bash
cd homeopathy_api
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

```bash
# Create database
createdb homeopathy_ai

# Or using psql:
psql -U postgres
CREATE DATABASE homeopathy_ai;
\q
```

### 3. Configure Environment

The `.env` file is already created with development defaults. Update it if needed:

```bash
# Edit .env and set your values (especially ANTHROPIC_API_KEY if using Claude)
```

### 4. Run the Application

```bash
# From the homeopathy_api directory
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (interactive API documentation)
- **ReDoc**: http://localhost:8000/redoc

## Using Docker (Recommended for Databases)

If you don't want to install PostgreSQL, Neo4j, and Redis locally, use Docker:

```bash
# Start PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16

# Create database
docker exec postgres createdb -U postgres homeopathy_ai

# Start Neo4j
docker run -d --name neo4j -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Start Redis
docker run -d --name redis -p 6379:6379 redis:latest
```

Then run the app as shown in step 4 above.

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
→ Run `pip install -r requirements.txt`

### "Connection refused" (PostgreSQL)
→ Make sure PostgreSQL is running: `psql -U postgres`

### "Connection refused" (Neo4j)
→ Make sure Neo4j is running on port 7687

### "Connection refused" (Redis)
→ Make sure Redis is running on port 6379

### "ANTHROPIC_API_KEY not set"
→ Add your API key to `.env` file, or the app will use rule-based responses

## API Endpoints

Once running, test the API:

```bash
# Create a session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "550e8400-e29b-41d4-a716-446655440000"}'

# Send a message
curl -X POST http://localhost:8000/api/v1/chat/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'

# View interactive docs
# Open http://localhost:8000/docs in your browser
```

## Next Steps

1. Check the API docs at http://localhost:8000/docs
2. Review the code structure in the folders
3. Configure your LLM provider (Anthropic, OpenAI, etc.)
4. Start building!
