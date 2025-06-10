#!/usr/bin/env python3
"""
Simple server startup script for development.
"""

import subprocess
import sys
from pathlib import Path


def check_redis():
    """Check if Redis is running."""
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("💡 Start Redis with: docker run -d -p 6379:6379 redis:7-alpine")
        return False


def create_env_file():
    """Create a basic .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# Database Configuration (for app metadata storage)
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pulse

# Redis Configuration (for connection storage)
REDIS_URL=redis://localhost:6379/0
"""
        env_file.write_text(env_content)
        print("✅ Created .env file - please update with your settings")
    else:
        print("✅ .env file exists")


def main():
    """Start the development server."""
    print("🚀 Starting Pulse Database Chat API")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)

    # Create env file if needed
    create_env_file()

    # Check Redis
    if not check_redis():
        print("\n⚠️  Redis is required but not running. Starting server anyway...")

    print("\n🔥 Starting FastAPI server...")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🧪 Run tests with: python test_api.py (in another terminal)")
    print("\n" + "=" * 40)

    # Start the server
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:server", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
