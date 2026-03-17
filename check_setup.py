#!/usr/bin/env python3
"""
Setup verification script — checks if all dependencies and services are available.
Run this before starting the app to diagnose issues.
"""

import sys
import subprocess
from pathlib import Path

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required (you have {version.major}.{version.minor})")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (run: pip install -r requirements.txt)")
        return False

def check_service(name, command, port=None):
    """Check if a service is running."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=2)
        if result.returncode == 0:
            if port:
                print(f"✅ {name} (port {port})")
            else:
                print(f"✅ {name}")
            return True
    except:
        pass
    
    if port:
        print(f"❌ {name} (port {port}) — not running")
    else:
        print(f"❌ {name} — not found")
    return False

def main():
    print("\n" + "="*50)
    print("🏥 Homeopathy AI Setup Verification")
    print("="*50 + "\n")

    all_ok = True

    # Check Python
    print("📌 Python:")
    all_ok &= check_python()
    print()

    # Check Python packages
    print("📌 Python Packages:")
    packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "pydantic",
        "dotenv",
    ]
    for pkg in packages:
        all_ok &= check_package(pkg)
    print()

    # Check services
    print("📌 External Services:")
    
    # PostgreSQL
    all_ok &= check_service(
        "PostgreSQL",
        "psql -U postgres -c 'SELECT 1' 2>/dev/null",
        5432
    )
    
    # Neo4j
    all_ok &= check_service(
        "Neo4j",
        "curl -s http://localhost:7474 > /dev/null",
        7687
    )
    
    # Redis
    all_ok &= check_service(
        "Redis",
        "redis-cli ping 2>/dev/null",
        6379
    )
    print()

    # Check .env file
    print("📌 Configuration:")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (will be created on startup)")
    print()

    # Summary
    print("="*50)
    if all_ok:
        print("✅ All checks passed! Ready to run.")
        print("\nStart the app with:")
        print("  Windows: run.bat")
        print("  Mac/Linux: ./run.sh")
    else:
        print("⚠️  Some checks failed. See above for details.")
        print("\nTo use Docker instead:")
        print("  docker-compose up -d")
        print("  Then run: run.bat (Windows) or ./run.sh (Mac/Linux)")
    print("="*50 + "\n")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
