import os
import sys

# Set up environment variables
os.environ["REDIS_HOST"] = "redis-11509.c90.us-east-1-3.ec2.redns.redis-cloud.com"
os.environ["REDIS_PORT"] = "11509"
os.environ["REDIS_USERNAME"] = "default"
os.environ["REDIS_PASSWORD"] = "aDevCXKeLli9kldGJccV15D1yS93Oyvd"
os.environ["REDIS_DB"] = "0"
os.environ["REDIS_SSL"] = "False"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCDR-02KzCcOwgcIGP1V4v_CiHcn3qwr1s"
os.environ["OPENAI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
os.environ["LANGCHAIN_API_KEY"] = os.environ["GOOGLE_API_KEY"]

# Replace flask.cli.load_dotenv with python-dotenv
try:
    from dotenv import load_dotenv
    if not load_dotenv():
        print("Warning: .env file not found, using environment variables set above")
except ImportError:
    print("python-dotenv not installed, using environment variables set above")

import traceback
from fastapi import FastAPI
from server.app import get_app
from fastapi.concurrency import asynccontextmanager

app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # try:
    #     # Set Langchain env variables
    #     config = load_config()
    #     if config.llm.langchain_tracing:
    #         os.environ["LANGSMITH_TRACING"] = 'true'
    #         os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    #         os.environ["LANGSMITH_API_KEY"] = config.llm.langchain_api_key.get_secret_value()
    #         os.environ["LANGSMITH_ENDPOINT"] = config.llm.langsmith_endpoint
    #         os.environ["LANGCHAIN_PROJECT"] = config.llm.langchain_project_name
    #         os.environ['OPENAI_API_KEY'] = config.llm.api_key.get_secret_value()
    #         print("Lifespan: Langchain environment variables set.")
    #     else:
    #         logging.info("Lifespan: Langchain tracing is disabled.")
    #         os.environ["LANGCHAIN_TRACING_V2"] = "false"
    # except Exception as e:
    #     print(f"Lifespan ERROR: Failed to set Langchain environment variables: {e}")

    # Skip Redis and AI agent initialization for student implementation
    print("🚀 Starting backend for student BB84 implementation...")
    print("   Skipping Redis and AI agent initialization for simplicity")
    
    # Check if student implementation is ready
    try:
        import json
        import os
        status_file = "student_implementation_status.json"
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status = json.load(f)
            if status.get("student_implementation_ready", False):
                print("✅ Student BB84 implementation detected and ready!")
            else:
                print("⚠️ Student implementation not ready - simulation will show implementation prompts")
        else:
            print("📝 No student implementation found - students need to implement BB84 first")
    except Exception as e:
        print(f"📝 Could not check student implementation status: {e}")

    yield
    # Shutdown
    print("🛑 Backend server shutting down...")

app = get_app(lifespan=lifespan)

if __name__ == '__main__':
    try:
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "5174"))  # Backend runs on 5174
        reload_flag = os.getenv("DEBUG", "True").lower() in ["true", "1", "t"]
        
        # Enable CORS for frontend
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",  # Frontend dev server
                "http://127.0.0.1:3000",
                "http://localhost:5174",  # Backend server
                "http://127.0.0.1:5174",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        print(f"Starting backend server on http://{host}:{port}")
        print("Make sure to start the frontend with 'npm run dev' in the ui directory")
        
        import uvicorn
        uvicorn.run(
            "start:app",
            host=host,
            port=port,
            reload=reload_flag
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"Server started on {host}:{port} with reload={reload_flag}")
