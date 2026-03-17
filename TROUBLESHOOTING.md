# 🔧 Troubleshooting Guide

Solutions to common issues.

---

## 🚀 Startup Issues

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

---

### Issue: "Connection refused" (PostgreSQL)

**Cause**: PostgreSQL not running

**Solutions**:

**Option 1: Check if running**
```bash
psql -U postgres
```

**Option 2: Start with Docker**
```bash
docker-compose up -d postgres
```

**Option 3: Install locally**
- [Download PostgreSQL](https://www.postgresql.org/download/)
- Follow installation instructions
- Create database: `createdb homeopathy_ai`

---

### Issue: "Connection refused" (Neo4j)

**Cause**: Neo4j not running

**Solutions**:

**Option 1: Check if running**
```bash
curl http://localhost:7474
```

**Option 2: Start with Docker**
```bash
docker-compose up -d neo4j
```

**Option 3: Install locally**
- [Download Neo4j](https://neo4j.com/download/)
- Follow installation instructions

---

### Issue: "Connection refused" (Redis)

**Cause**: Redis not running

**Solutions**:

**Option 1: Check if running**
```bash
redis-cli ping
```

**Option 2: Start with Docker**
```bash
docker-compose up -d redis
```

**Option 3: Install locally**
- [Download Redis](https://redis.io/download)
- Follow installation instructions

---

### Issue: "Port 8000 already in use"

**Cause**: Another app is using port 8000

**Solutions**:

**Option 1: Use a different port**
```bash
python -m uvicorn main:app --port 8001
```

**Option 2: Kill the process using port 8000**

**Windows**:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux**:
```bash
lsof -i :8000
kill -9 <PID>
```

---

### Issue: "DATABASE_URL not set"

**Cause**: `.env` file missing or not configured

**Solution**:
```bash
# Create .env from template
cp .env.example .env

# Edit .env and set DATABASE_URL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/homeopathy_ai
```

---

### Issue: "ANTHROPIC_API_KEY not set"

**Cause**: LLM API key not configured

**Solution**:
```bash
# Edit .env and add your API key
ANTHROPIC_API_KEY=sk-ant-...
```

**Note**: The app will work without it (using rule-based responses).

---

## 🐛 Runtime Issues

### Issue: "No such table: sessions"

**Cause**: Database tables not created

**Solution**:
The tables should be created automatically on startup. If not:

```bash
# Delete and recreate
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

### Issue: "Session not found"

**Cause**: Invalid session ID

**Solution**:
- Create a new session first
- Use the correct session ID from the response

---

### Issue: "No rubrics collected yet"

**Cause**: Trying to analyze before collecting symptoms

**Solution**:
- Send messages to collect symptoms first
- Wait until `analysis_ready` is `true`
- Then trigger analysis

---

### Issue: "Connection timeout"

**Cause**: Services taking too long to respond

**Solution**:
- Check if services are running
- Increase timeout in `.env`
- Restart services

---

## 🔍 Debugging

### Enable Debug Mode

Edit `.env`:
```env
DEBUG=true
```

This will:
- Show detailed error messages
- Enable SQL query logging
- Show request/response details

---

### Check Setup

Run the verification script:
```bash
python check_setup.py
```

This will tell you:
- ✅ Python version
- ✅ Installed packages
- ✅ Running services
- ✅ Configuration files

---

### View Logs

**Server logs**:
- Check the terminal where the server is running

**Docker logs**:
```bash
docker-compose logs -f
```

**Specific service**:
```bash
docker-compose logs -f postgres
docker-compose logs -f neo4j
docker-compose logs -f redis
```

---

### Test Database Connection

```python
import asyncio
from core.database import engine

async def test_db():
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        print("Database connection OK")

asyncio.run(test_db())
```

---

## 🐳 Docker Issues

### Issue: "docker-compose: command not found"

**Cause**: Docker Compose not installed

**Solution**:
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Or install Docker Compose separately

---

### Issue: "Cannot connect to Docker daemon"

**Cause**: Docker not running

**Solution**:
- Start Docker Desktop
- Or start Docker service

---

### Issue: "Port already in use"

**Cause**: Docker container already running

**Solution**:
```bash
# Stop all containers
docker-compose down

# Or stop specific container
docker stop <container_id>
```

---

### Issue: "Out of disk space"

**Cause**: Docker images/containers taking up space

**Solution**:
```bash
# Clean up unused images
docker image prune

# Clean up unused containers
docker container prune

# Clean up everything
docker system prune -a
```

---

## 🔄 Reset Everything

### Option 1: Soft Reset (Keep data)
```bash
# Stop server
# Press Ctrl+C

# Restart
python -m uvicorn main:app --reload
```

---

### Option 2: Hard Reset (Delete data)

**With Docker**:
```bash
# Stop and remove containers
docker-compose down -v

# Start fresh
docker-compose up -d
```

**Without Docker**:
```bash
# Delete database
dropdb homeopathy_ai

# Recreate database
createdb homeopathy_ai

# Restart server
python -m uvicorn main:app --reload
```

---

### Option 3: Complete Reset

```bash
# Remove virtual environment
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

# Remove .env
rm .env  # Mac/Linux
del .env  # Windows

# Remove cache
find . -type d -name __pycache__ -exec rm -rf {} +  # Mac/Linux

# Start fresh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

---

## 📞 Getting Help

1. **Check this guide** — Most issues are covered here
2. **Run `check_setup.py`** — Diagnose your setup
3. **Check the logs** — Look for error messages
4. **Read the code** — Check comments in the files
5. **Check the API docs** — http://localhost:8000/docs

---

## 💡 Pro Tips

- Always check if services are running first
- Use Docker if you don't want to install databases
- Enable DEBUG mode for detailed error messages
- Keep the server running while developing
- Use the API docs to test endpoints

---

## 🎯 Common Solutions

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start services: `docker-compose up -d` |
| "ModuleNotFoundError" | Install dependencies: `pip install -r requirements.txt` |
| "Port already in use" | Use different port: `--port 8001` |
| "Database error" | Check `.env` DATABASE_URL |
| "API not responding" | Check if server is running |
| "No rubrics collected" | Send messages first |
| "Session not found" | Create new session |

---

**Still stuck? Run `python check_setup.py` to diagnose! 🔍**
