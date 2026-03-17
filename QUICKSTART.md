# 🚀 Quick Start Guide

## For Windows Users

1. **Open Command Prompt** in the `homeopathy_api` folder
2. **Run this command:**
   ```
   run.bat
   ```
3. **Wait for setup** — it will install everything automatically
4. **Open your browser** to http://localhost:8000/docs

That's it! The API is running.

---

## For Mac/Linux Users

1. **Open Terminal** in the `homeopathy_api` folder
2. **Run this command:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. **Wait for setup** — it will install everything automatically
4. **Open your browser** to http://localhost:8000/docs

That's it! The API is running.

---

## What You Need First

Before running, make sure you have:

- **Python 3.10 or higher** — [Download](https://www.python.org/downloads/)
- **PostgreSQL** — [Download](https://www.postgresql.org/download/) OR use Docker
- **Neo4j** — [Download](https://neo4j.com/download/) OR use Docker
- **Redis** — [Download](https://redis.io/download) OR use Docker

### Using Docker (Easier - No Installation Needed)

If you have Docker installed, run these commands in a terminal:

```bash
# PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
docker exec postgres createdb -U postgres homeopathy_ai

# Neo4j
docker run -d --name neo4j -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Redis
docker run -d --name redis -p 6379:6379 redis:latest
```

Then run `run.bat` (Windows) or `./run.sh` (Mac/Linux).

---

## Testing the API

Once running, open http://localhost:8000/docs in your browser. You'll see an interactive API explorer where you can test all endpoints.

### Quick Test:

1. Click on **POST /api/v1/sessions**
2. Click **Try it out**
3. Click **Execute**
4. Copy the `session_id` from the response
5. Go to **POST /api/v1/chat/{session_id}/message**
6. Paste the `session_id` and type a message like "I have a headache"
7. Click **Execute**

---

## Troubleshooting

### "Connection refused" errors?
- Make sure PostgreSQL, Neo4j, and Redis are running
- If using Docker, check: `docker ps`

### "ModuleNotFoundError"?
- The script should install dependencies automatically
- If not, run: `pip install -r requirements.txt`

### Port 8000 already in use?
- Edit `run.bat` or `run.sh` and change `--port 8000` to another port like `8001`

### Need to stop the server?
- Press **Ctrl+C** in the terminal

---

## Next Steps

1. **Explore the API** at http://localhost:8000/docs
2. **Read the code** in the folders (api/, services/, database/)
3. **Configure LLM** — Add your Anthropic API key to `.env`
4. **Check SETUP.md** for more detailed information

---

## File Structure

```
homeopathy_api/
├── main.py                 ← Start here (FastAPI app)
├── run.bat / run.sh        ← Use this to start
├── .env                    ← Your configuration
├── requirements.txt        ← Python dependencies
├── core/                   ← Database & config
├── database/               ← Data models
├── models/                 ← Request/response schemas
├── api/                    ← API endpoints
├── services/               ← Business logic
└── llm/                    ← AI integration
```

---

## Questions?

- Check the API docs: http://localhost:8000/docs
- Read SETUP.md for detailed setup
- Check the code comments in each file
