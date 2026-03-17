# 🎯 First Run Guide

This is your guide for the very first time running Homeopathy AI.

---

## ⏱️ Time Required

- **Windows**: 5 minutes
- **Mac/Linux**: 5 minutes
- **Docker**: 10 minutes

---

## 🪟 Windows Users

### Step 1: Open Command Prompt
1. Press `Win + R`
2. Type `cmd`
3. Press Enter

### Step 2: Navigate to Project
```bash
cd homeopathy_api
```

### Step 3: Run the Startup Script
```bash
run.bat
```

### Step 4: Wait for Setup
You'll see:
```
🏥 Starting Homeopathy AI API...
📦 Creating virtual environment...
📚 Installing dependencies...
✅ Setup complete!
🚀 Starting server on http://localhost:8000
```

### Step 5: Open Your Browser
Go to: **http://localhost:8000/docs**

You should see the interactive API documentation!

### Step 6: Test It
1. Click **POST /api/v1/sessions**
2. Click **Try it out**
3. Click **Execute**
4. You should get a response with a `session_id`

**Done! 🎉**

---

## 🍎 Mac/Linux Users

### Step 1: Open Terminal
1. Press `Cmd + Space` (Mac) or `Ctrl + Alt + T` (Linux)
2. Type `terminal`
3. Press Enter

### Step 2: Navigate to Project
```bash
cd homeopathy_api
```

### Step 3: Make Script Executable
```bash
chmod +x run.sh
```

### Step 4: Run the Startup Script
```bash
./run.sh
```

### Step 5: Wait for Setup
You'll see:
```
🏥 Starting Homeopathy AI API...
📦 Creating virtual environment...
📚 Installing dependencies...
✅ Setup complete!
🚀 Starting server on http://localhost:8000
```

### Step 6: Open Your Browser
Go to: **http://localhost:8000/docs**

You should see the interactive API documentation!

### Step 7: Test It
1. Click **POST /api/v1/sessions**
2. Click **Try it out**
3. Click **Execute**
4. You should get a response with a `session_id`

**Done! 🎉**

---

## 🐳 Docker Users (Any OS)

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 1: Start Services
```bash
cd homeopathy_api
docker-compose up -d
```

### Step 2: Wait 30 Seconds
Services are starting in the background.

### Step 3: Run the App
```bash
# Windows
run.bat

# Mac/Linux
./run.sh
```

### Step 4: Open Your Browser
Go to: **http://localhost:8000/docs**

You should see the interactive API documentation!

### Step 5: Test It
1. Click **POST /api/v1/sessions**
2. Click **Try it out**
3. Click **Execute**
4. You should get a response with a `session_id`

**Done! 🎉**

---

## ✅ Verify It's Working

### Check 1: Server is Running
Open http://localhost:8000/health in your browser.

You should see:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Check 2: API Docs are Available
Open http://localhost:8000/docs in your browser.

You should see the Swagger UI with all endpoints listed.

### Check 3: Create a Session
1. Open http://localhost:8000/docs
2. Click **POST /api/v1/sessions**
3. Click **Try it out**
4. Click **Execute**
5. You should get a response like:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": null,
  "status": "active",
  "stage": "initial",
  "created_at": "2026-03-17T01:50:00",
  "updated_at": "2026-03-17T01:50:00"
}
```

---

## 🆘 Something Went Wrong?

### "Connection refused"
**Problem**: Services aren't running

**Solution**:
- Use Docker: `docker-compose up -d`
- Or install PostgreSQL, Neo4j, Redis locally

### "ModuleNotFoundError"
**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
**Problem**: Another app is using port 8000

**Solution**:
Edit `run.bat` or `run.sh` and change `--port 8000` to `--port 8001`

### "Still stuck?"
Run this to diagnose:
```bash
python check_setup.py
```

This will tell you what's missing.

---

## 🎓 What to Do Next

### Option 1: Explore the API
1. Open http://localhost:8000/docs
2. Try different endpoints
3. Create a session and send messages

### Option 2: Read the Code
1. Open `main.py` in your editor
2. Explore the folders: `api/`, `services/`, `database/`
3. Read the comments in each file

### Option 3: Configure LLM
1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Edit `.env` and add: `ANTHROPIC_API_KEY=your-key`
3. Restart the server

### Option 4: Read the Documentation
- **README.md** — Full project documentation
- **INSTALLATION_GUIDE.md** — Detailed setup guide
- **SETUP.md** — Technical setup details

---

## 🛑 How to Stop the Server

Press **Ctrl+C** in the terminal where the server is running.

You'll see:
```
🛑 Server stopped
```

---

## 🔄 Running Again

Next time you want to run the server:

```bash
cd homeopathy_api

# Windows
run.bat

# Mac/Linux
./run.sh

# Any OS
python start.py
```

It will be much faster (no setup needed).

---

## 📚 Documentation

- **START_HERE.md** — Quick overview
- **QUICKSTART.md** — 5-minute setup
- **INSTALLATION_GUIDE.md** — Complete guide
- **README.md** — Full documentation
- **SETUP.md** — Technical details

---

## 💡 Pro Tips

1. **Keep the server running** while you develop
2. **Use the API docs** at http://localhost:8000/docs to test endpoints
3. **Check `.env`** if you get configuration errors
4. **Use Docker** if you don't want to install databases
5. **Run `check_setup.py`** to diagnose issues

---

## 🎉 Congratulations!

You've successfully set up Homeopathy AI! 

Now you can:
- ✅ Explore the API
- ✅ Read the code
- ✅ Customize the configuration
- ✅ Build on top of it

**Happy coding! 🚀**

---

## 📞 Need More Help?

1. Check the documentation files
2. Review the API docs at http://localhost:8000/docs
3. Check the code comments
4. Run `python check_setup.py` to diagnose issues

---

**You're all set! Enjoy! 🏥**
