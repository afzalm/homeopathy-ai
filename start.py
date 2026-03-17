#!/usr/bin/env python3
"""
Simple Python startup script for Homeopathy AI.
Run this instead of run.bat or run.sh if you prefer.

Usage:
    python start.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("🏥 Homeopathy AI - Starting Server")
    print("="*60 + "\n")

    # Check Python version
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)

    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from .env.example...")
        env_example = Path(".env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ .env created\n")
        else:
            print("❌ .env.example not found\n")
            sys.exit(1)

    # Install dependencies
    print("📚 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Dependencies already installed\n")
    except ImportError:
        print("📦 Installing dependencies...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            capture_output=True
        )
        if result.returncode != 0:
            print("❌ Failed to install dependencies")
            print(result.stderr.decode())
            sys.exit(1)
        print("✅ Dependencies installed\n")

    # Start the server
    print("🚀 Starting server on http://localhost:8000")
    print("📖 API docs available at http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*60 + "\n")

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
