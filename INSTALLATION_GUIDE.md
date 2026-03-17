# 📦 Installation & Setup Guide

Complete guide to get Homeopathy AI running on your system.

---

## 🎯 Choose Your Path

### Path 1: Fastest (Recommended for Most Users)
**Time: 5 minutes**
- Uses startup scripts
- Automatic dependency installation
- Automatic database setup

### Path 2: Docker (Recommended for Production)
**Time: 10 minutes**
- No local database installation needed
- Isolated environments
- Easy cleanup

### Path 3: Manual (For Advanced Users)
**Time: 15 minutes**
- Full control
- Manual dependency management
- Manual database setup

---

## 🚀 Path 1: Fastest Setup

### Windows

1. **Open Command Prompt** in the `homeopathy_api` folder
2. **Run:**
   ```bash
   run.bat
   ```
3. **Wait** for setup to complete (2-3 minutes)
4. **Open browser** to http://localhost:8000/docs

### Mac/Linux

1. **Open Terminal** in the `homeopathy_api` folder
2. **Run:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. **Wait** for setup to complete (2-3 minutes)
4. **Open browser** to http://localhost:8000/docs

### What Happens Automatically
- ✅ Python virtual environment created
- ✅ Dependencies installed
- ✅ `.env` configuration created
- ✅ Database tables created
- ✅ Server started on port 8000

---

## 🐳 Path 2: Docker Setup

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Steps

1. **Open Terminal/Command Prompt** in the `homeopathy_api` folder

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Wait 30 seconds** for services to start

4. **Start the app:**
   ```bash
   # Windows
   run.bat
   
   # Mac/Linux
   ./run.sh
   ```

5. **Open browser** to http://localhost:8000/docs

### Useful Docker Commands

```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

## 🔧 Path 3: Manual Setup

### Prerequisites

Install these on your system:

1. **Python 3.10+**
   - [Download](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **PostgreSQL 12+**
   - [Download](https://www.postgresql.org/download/)
   - Verify: `psql --version`

3. **Neo4j 4.4+**
   - [Download](https://neo4j.com/download/)
   - Verify: Open http://localhost:7474

4. **Redis 6+**
   - [Download](https://redis.io/download)
   - Verify: `redis-cli ping`

### Setup Steps

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate it:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create database:**
   ```bash
   createdb homeopathy_ai
   ```

5. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

6. **Start the server:**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Open browser** to http://localhost:8000/docs

---

## ✅ Verify Installation

### Quick Check

Run this to verify everything is set up:

```bash
python check_setup.py
```

This will tell you:
- ✅ Python version
- ✅ Installed packages
- ✅ Running services
- ✅ Configuration files

### Test the API

1. Open http://localhost:8000/docs
2. Click **POST /api/v1/sessions**
3. Click **Try it out** → **Execute**
4. You should get a response with a `session_id`

---

## 🆘 Troubleshooting

### "Connection refused" (PostgreSQL)

**Problem:** Can't connect to PostgreSQL

**Solutions:**
```bash
# Check if running
psql -U postgres

# Or start with Docker
docker-compose up -d postgres
```

### "Connection refused" (Neo4j)

**Problem:** Can't connect to Neo4j

**Solutions:**
```bash
# Check if running
curl http://localhost:7474

# Or start with Docker
docker-compose up -d neo4j
```

### "Connection refused" (Redis)

**Problem:** Can't connect to Redis

**Solutions:**
```bash
# Check if running
redis-cli ping

# Or start with Docker
docker-compose up -d redis
```

### "ModuleNotFoundError: No module named 'fastapi'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Problem:** Another app is using port 8000

**Solutions:**
```bash
# Option 1: Use a different port
python -m uvicorn main:app --port 8001

# Option 2: Kill the process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### "DATABASE_URL not set"

**Problem:** `.env` file missing or not configured

**Solution:**
```bash
# Create .env from template
cp .env.example .env

# Edit .env and set DATABASE_URL
```

### "ANTHROPIC_API_KEY not set"

**Problem:** LLM API key not configured

**Solution:**
```bash
# Edit .env and add your API key
ANTHROPIC_API_KEY=sk-ant-...
```

The app will work without it (using rule-based responses).

---

## 🔄 Updating Dependencies

If you need to update packages:

```bash
# Upgrade pip
pip install --upgrade pip

# Install latest versions
pip install -r requirements.txt --upgrade
```

---

## 🧹 Cleanup

### Remove Virtual Environment
```bash
# Windows
rmdir /s venv

# Mac/Linux
rm -rf venv
```

### Stop Docker Services
```bash
docker-compose down
```

### Remove Docker Data
```bash
docker-compose down -v
```

---

## 📝 Configuration

Edit `.env` to customize:

```env
# App
DEBUG=true                    # Enable debug mode
SECRET_KEY=your-secret-key   # Change in production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/homeopathy_ai

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379

# LLM
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key

# Ranking
WEIGHT_REPERTORY=0.50
WEIGHT_RAG=0.30
WEIGHT_OUTCOME=0.20
```

---

## 🎯 Next Steps

1. **Verify installation** → Run `python check_setup.py`
2. **Start the server** → Use one of the 3 paths above
3. **Test the API** → Open http://localhost:8000/docs
4. **Read the code** → Explore the folders
5. **Customize** → Edit `.env` and modify code

---

## 📚 Additional Resources

- **START_HERE.md** — Quick overview
- **QUICKSTART.md** — 5-minute setup
- **README.md** — Full documentation
- **API Docs** — http://localhost:8000/docs (when running)

---

## 💡 Tips

- **Use Docker** if you don't want to install databases locally
- **Use Path 1** if you want the fastest setup
- **Use Path 3** if you need full control
- **Run `check_setup.py`** to diagnose issues
- **Check `.env`** if you get configuration errors

---

**Ready? Pick a path above and get started! 🚀**
