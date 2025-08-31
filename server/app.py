from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.socket_server.socket_server import websocket_endpoint

REACT_BUILD_FOLDER = "../ui/dist"

# Create a new app factory function
def get_app(lifespan):
    app = FastAPI(title="Network Simulator API", version="1.0.0", lifespan=lifespan)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with your Netlify domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    from server.routes import register_routes
    register_routes(app)
    
    app.add_websocket_route("/api/ws", websocket_endpoint)
    
    return app
