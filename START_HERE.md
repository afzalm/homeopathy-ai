# 🚀 START HERE

## You have 3 options to run this app:

---

## Option 1: Easiest (Recommended for Beginners)

### Windows
1. Double-click `run.bat`
2. Wait for setup to complete
3. Open http://localhost:8000/docs

### Mac/Linux
1. Open Terminal in this folder
2. Run: `chmod +x run.sh && ./run.sh`
3. Open http://localhost:8000/docs

**This option automatically:**
- Creates a Python virtual environment
- Installs all dependencies
- Creates `.env` configuration
- Starts the server

---

## Option 2: Using Docker (Best for Production)

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Steps
1. Open Terminal/Command Prompt in this folder
2. Run: `docker-compose up -d`
3. Wait 30 seconds for services to start
4. Run: `run.bat` (Windows) or `./run.sh` (Mac/Linux)
5. Open http://localhost:8000/docs

**This option:**
- Starts PostgreSQL, Neo4j, and Redis in containers
- No local installation needed
- Perfect for development and testing

---

## Option 3: Manual Setup (For Advanced Users)

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Neo4j 4.4+
- Redis 6+

### Steps
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verify Setup

Before running, check if everything is ready:

```bash
python check_setup.py
```

This will tell you what's missing.

---

## 🌐 Access the API

Once running, open your browser:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute quick start
- **[SETUP.md](SETUP.md)** — Detailed setup guide
- **[README.md](README.md)** — Full project documentation

---

## 🆘 Troubleshooting

### "Connection refused" errors?
→ Services (PostgreSQL, Neo4j, Redis) aren't running
→ Use Option 2 (Docker) to start them automatically

### "ModuleNotFoundError"?
→ Dependencies not installed
→ Run: `pip install -r requirements.txt`

### Port 8000 already in use?
→ Edit `run.bat` or `run.sh`
→ Change `--port 8000` to `--port 8001`

### Still stuck?
→ Check [SETUP.md](SETUP.md) for detailed troubleshooting

---

## 🎯 Next Steps

1. **Start the app** using one of the 3 options above
2. **Open the API docs** at http://localhost:8000/docs
3. **Test an endpoint** — try creating a session
4. **Explore the code** in the folders
5. **Read the documentation** in the files above

---

## 📁 What's in Each Folder?

```
homeopathy_api/
├── api/          ← API endpoints (routes)
├── services/     ← Business logic
├── database/     ← Data models
├── models/       ← Request/response schemas
├── core/         ← Configuration & database setup
└── llm/          ← AI integration
```

---

## 💡 Quick Test

Once running, test the API:

1. Open http://localhost:8000/docs
2. Click **POST /api/v1/sessions**
3. Click **Try it out** → **Execute**
4. Copy the `session_id` from the response
5. Click **POST /api/v1/chat/{session_id}/message**
6. Paste the `session_id` and type: "I have a headache"
7. Click **Execute**

You should get an AI response!

---

## 🎓 Learning Path

1. **Understand the flow** → Read [README.md](README.md)
2. **Get it running** → Follow one of the 3 options above
3. **Explore the API** → Use http://localhost:8000/docs
4. **Read the code** → Start with `main.py`, then explore folders
5. **Customize it** → Edit `.env` and modify code as needed

---

**Ready? Pick an option above and get started! 🚀**
