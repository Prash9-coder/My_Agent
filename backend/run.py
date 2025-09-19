#!/usr/bin/env python3
"""
AI English Tutor Backend Server
Run this script to start the FastAPI backend server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Main function to run the server"""
    # Load environment variables
    from dotenv import load_dotenv
    env_file = backend_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}. Using defaults.")
        print("💡 Create a .env file from .env.example for custom configuration")
    
    # Configuration
    host = os.getenv('API_HOST', 'localhost')
    port = int(os.getenv('API_PORT', '8000'))
    # Disable reload in Replit environment to avoid process tracking issues
    reload = False
    
    print(f"🚀 Starting AI English Tutor Backend Server...")
    print(f"📡 Server will be available at: http://{host}:{port}")
    print(f"📚 API documentation at: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print(f"🌍 CORS origins: {os.getenv('CORS_ORIGINS', 'http://localhost:3000')}")
    
    # Check if Google Cloud credentials are set up
    gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if gcp_creds and os.path.exists(gcp_creds):
        print(f"☁️  Google Cloud credentials found: {gcp_creds}")
    else:
        print("⚠️  Google Cloud credentials not found. Speech services will use mock implementations.")
        print("💡 Set GOOGLE_APPLICATION_CREDENTIALS environment variable for full functionality")
    
    print("=" * 80)
    
    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=os.getenv('LOG_LEVEL', 'info').lower()
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()