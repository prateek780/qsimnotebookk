from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.socket_server.socket_server import websocket_endpoint

REACT_BUILD_FOLDER = "../ui/dist"

# Create a new app factory function
def get_app(lifespan):
    app = FastAPI(title="Network Simulator API", version="1.0.0", lifespan=lifespan)
    
    # Add CORS middleware with specific configuration for WebSocket
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Register routes
    from server.routes import register_routes
    register_routes(app)
    
    # Add WebSocket route with explicit configuration
    from fastapi import WebSocket
    @app.websocket("/ws")  # Changed from /api/ws to /ws
    async def websocket_route(websocket: WebSocket):
        await websocket_endpoint(websocket)
        
    @app.websocket("/api/ws")  # Keep old endpoint for compatibility
    async def websocket_route_api(websocket: WebSocket):
        await websocket_endpoint(websocket)
    
    # Add route for simulation status
    @app.get("/api/simulation/status")
    async def get_simulation_status():
        try:
            with open('simulation.log', 'r') as f:
                import json
                logs = [json.loads(line) for line in f]
                return {"status": "success", "logs": logs}
        except FileNotFoundError:
            return {"status": "no_logs"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    return app
