# 📚 Complete Documentation Index

All documentation files for Homeopathy AI.

---

## 🚀 Getting Started (Start Here!)

### For First-Time Users
1. **[FIRST_RUN.md](FIRST_RUN.md)** ⭐ START HERE
   - Step-by-step first run guide
   - Platform-specific instructions (Windows, Mac, Linux)
   - Verification steps
   - Time: 5 minutes

2. **[START_HERE.md](START_HERE.md)**
   - 30-second overview
   - 3 ways to run the app
   - Quick links

3. **[QUICKSTART.md](QUICKSTART.md)**
   - 5-minute quick start
   - Using Docker
   - Testing the API

---

## 📖 Installation & Setup

### Detailed Setup Guides
1. **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**
   - Complete installation guide
   - All 3 installation paths (Fastest, Docker, Manual)
   - Prerequisites for each path
   - Troubleshooting

2. **[SETUP.md](SETUP.md)**
   - Detailed technical setup
   - Configuration options
   - Database setup
   - LLM configuration

---

## 🧪 Testing & API

### API Documentation
1. **[API_TESTING.md](API_TESTING.md)**
   - Complete API testing guide
   - Interactive testing (easiest)
   - Testing workflow
   - cURL examples
   - Python examples
   - Testing scenarios
   - Verification checklist

2. **[README.md](README.md)**
   - Full project documentation
   - Architecture overview
   - API endpoints reference
   - Data flow explanation
   - Security information

---

## 🔧 Troubleshooting & Help

### Problem Solving
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
   - Solutions to common issues
   - Startup issues
   - Runtime issues
   - Docker issues
   - Debugging tips
   - Reset procedures
   - Common solutions table

---

## 📁 Project Structure

### Code Organization
```
homeopathy_api/
├── main.py                  ← FastAPI app entry point
├── requirements.txt         ← Python dependencies
├── .env                     ← Configuration
├── docker-compose.yml       ← Docker services
│
├── core/                    ← Configuration & database
│   ├── config.py            ← Settings
│   └── database.py          ← Database setup
│
├── database/                ← Data models
│   └── models.py            ← ORM models
│
├── models/                  ← Request/response schemas
│   └── schemas.py           ← Pydantic schemas
│
├── api/                     ← API endpoints
│   ├── session_routes.py    ← Session endpoints
│   ├── chat_routes.py       ← Chat endpoints
│   ├── remedy_routes.py     ← Remedy endpoints
│   └── case_routes.py       ← Case endpoints
│
├── services/                ← Business logic
│   ├── session_manager.py   ← Core orchestration
│   ├── symptom_extractor.py ← Symptom extraction
│   ├── repertory_engine.py  ← Remedy scoring
│   ├── rag_service.py       ← Materia Medica retrieval
│   └── remedy_ranker.py     ← Remedy ranking
│
└── llm/                     ← AI integration
    └── case_agent.py        ← AI conversation
```

---

## 🛠️ Utility Files

### Helper Scripts & Configuration
- **run.bat** — Windows startup script
- **run.sh** — Mac/Linux startup script
- **start.py** — Python startup script
- **check_setup.py** — Setup verification
- **Makefile** — Common commands
- **pytest.ini** — Test configuration
- **.gitignore** — Git ignore rules
- **docker-compose.yml** — Docker services

---

## 📋 Quick Reference

### Common Commands

| Task | Command |
|------|---------|
| Run (Windows) | `run.bat` |
| Run (Mac/Linux) | `./run.sh` |
| Run (Any OS) | `python start.py` |
| Verify setup | `python check_setup.py` |
| Start Docker | `docker-compose up -d` |
| Stop Docker | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Install deps | `pip install -r requirements.txt` |
| Install dev deps | `pip install -r requirements-dev.txt` |

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session |
| GET | `/api/v1/sessions/{id}/state` | Get session state |
| POST | `/api/v1/chat/{id}/message` | Send message |
| POST | `/api/v1/chat/{id}/analyse` | Analyze symptoms |
| GET | `/api/v1/chat/{id}/history` | Get history |
| GET | `/api/v1/remedies` | List remedies |
| GET | `/api/v1/remedies/{id}` | Get remedy |
| POST | `/api/v1/cases` | Create case |
| GET | `/api/v1/cases/{id}` | Get case |

### URLs

| Purpose | URL |
|---------|-----|
| Interactive API Docs | http://localhost:8000/docs |
| Alternative API Docs | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Neo4j Browser | http://localhost:7474 |

---

## 🎓 Learning Path

### For Beginners
1. Read **FIRST_RUN.md** (5 min)
2. Run the app using startup script (5 min)
3. Open http://localhost:8000/docs (2 min)
4. Test creating a session (2 min)
5. Read **README.md** (15 min)

### For Developers
1. Read **README.md** (15 min)
2. Read **INSTALLATION_GUIDE.md** (10 min)
3. Explore the code structure (15 min)
4. Read **API_TESTING.md** (10 min)
5. Test the API endpoints (15 min)

### For DevOps
1. Read **INSTALLATION_GUIDE.md** (10 min)
2. Set up Docker: `docker-compose up -d` (5 min)
3. Configure `.env` (5 min)
4. Run the app (5 min)
5. Check logs: `docker-compose logs -f` (ongoing)

---

## 🆘 Finding Help

### By Problem Type

**Can't get it running?**
→ Read [FIRST_RUN.md](FIRST_RUN.md)

**Setup issues?**
→ Read [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

**Errors or crashes?**
→ Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Want to test the API?**
→ Read [API_TESTING.md](API_TESTING.md)

**Need full documentation?**
→ Read [README.md](README.md)

**Want to understand the code?**
→ Read [README.md](README.md) then explore the code

---

## 📞 Support Resources

1. **Documentation** — All files in this directory
2. **API Docs** — http://localhost:8000/docs (when running)
3. **Setup Verification** — `python check_setup.py`
4. **Code Comments** — Check comments in each file
5. **Troubleshooting** — [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ✅ Checklist

Before you start:
- ✅ Read [FIRST_RUN.md](FIRST_RUN.md)
- ✅ Have Python 3.10+ installed
- ✅ Have Docker installed (or databases)
- ✅ Have 5 minutes to set up

---

## 🎯 Next Steps

1. **Choose your path**:
   - Beginner? → Read [FIRST_RUN.md](FIRST_RUN.md)
   - Developer? → Read [README.md](README.md)
   - DevOps? → Read [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

2. **Run the app**:
   ```bash
   # Windows
   run.bat
   
   # Mac/Linux
   ./run.sh
   
   # Any OS
   python start.py
   ```

3. **Test the API**:
   - Open http://localhost:8000/docs
   - Follow [API_TESTING.md](API_TESTING.md)

4. **Explore the code**:
   - Start with `main.py`
   - Then explore the folders

---

## 📚 File Organization

### Root Directory
- **README_FIRST.md** — Start here (in parent directory)
- **COMPLETE_SUMMARY.md** — Setup summary (in parent directory)
- **GETTING_STARTED.md** — Getting started (in parent directory)
- **SETUP_COMPLETE.md** — Setup completion (in parent directory)

### homeopathy_api/ Directory
- **FIRST_RUN.md** ⭐ — Step-by-step first run
- **START_HERE.md** — Quick overview
- **QUICKSTART.md** — 5-minute setup
- **INSTALLATION_GUIDE.md** — Complete installation
- **SETUP.md** — Technical setup
- **README.md** — Full documentation
- **API_TESTING.md** — API testing guide
- **TROUBLESHOOTING.md** — Problem solving
- **INDEX.md** — This file

---

## 🎉 Ready?

**Start here**: [FIRST_RUN.md](FIRST_RUN.md)

Then run:
```bash
# Windows
run.bat

# Mac/Linux
./run.sh

# Any OS
python start.py
```

**Happy coding! 🚀**
