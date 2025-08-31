import os
import sys

# Set up environment variables
os.environ["REDIS_HOST"] = "redis-11509.c90.us-east-1-3.ec2.redns.redis-cloud.com"
os.environ["REDIS_PORT"] = "11509"
os.environ["REDIS_USERNAME"] = "default"
os.environ["REDIS_PASSWORD"] = "aDevCXKeLli9kldGJccV15D1yS93Oyvd"
os.environ["REDIS_DB"] = "0"
os.environ["REDIS_SSL"] = "False"
os.environ["GOOGLE_API_KEY"] = "Insert API key here"
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

    try:
        from data.models.connection.redis import get_redis_conn
        if get_redis_conn().ping():
            print("Successfully connected to Redis!")
        else:
            raise Exception("Failed to connect to Redis")

    except Exception as e:
        print(f"Lifespan ERROR: Failed to connect to Redis: {e}")
        sys.exit(1)

    try:
        from ai_agent.src.orchestration.coordinator import Coordinator
        # Initialize the Coordinate class
        await Coordinator().initialize_system()
        print("Successfully initialized Coordinator")
    except Exception as e:
        traceback.print_exc()
        print(f"Lifespan ERROR: Failed to initialize Coordinate class: {e}")
        sys.exit(1)

    try:
        from data.models.connection.redis import get_redis_conn
        from data.embedding.vector_log import VectorLogEntry
        VectorLogEntry.create_index(get_redis_conn())
        print("Successfully created VectorLogEntry index")
    except Exception as e:
        traceback.print_exc()
        print(f"Lifespan ERROR: Failed to create VectorLogEntry index: {e}")

    yield
    # Shutdown
    print("Lifespan: Disconnecting from Redis...")
    try:
        redis_conn = get_redis_conn()
        if redis_conn:
            redis_conn.close()
            print("Lifespan: Disconnected from Redis.")
        else:
            print("Lifespan: No Redis connection to close.")
    except Exception as e:
        print(f"Lifespan ERROR: Failed to disconnect from Redis: {e}")

app = get_app(lifespan=lifespan)

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    # Use Railway's PORT env var in production, fallback to 5174 for local development
    port = int(os.getenv("PORT", "5174"))
    reload_flag = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
    
    print(f"Starting server on {host}:{port} with reload={reload_flag}")
    
    import uvicorn
    uvicorn.run(
        "start:app",
        host=host,
        port=port,
        reload=reload_flag
    )
