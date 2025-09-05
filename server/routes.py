import os
from fastapi import APIRouter, FastAPI, Request, Response

from fastapi.responses import StreamingResponse
import httpx

from config.config import get_config


def proxy_to_live_app(app):
    REACT_DEV_SERVER_URL = "http://localhost:3000"
    async_client = httpx.AsyncClient(base_url=REACT_DEV_SERVER_URL)

    @app.api_route(
        "/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    )
    async def proxy_to_react(path: str, request: Request):
        """
        Proxies requests to the React development server.
        """
        # Construct the target URL within the React dev server
        # httpx handles joining the base_url with the relative path
        url = httpx.URL(path=f"/{path}", query=request.url.query.encode("utf-8"))

        # Prepare the request for forwarding
        fwd_request = async_client.build_request(
            method=request.method,
            url=url,
            headers={
                k: v for k, v in request.headers.items() if k.lower() != "host"
            },  # Exclude host header
            content=await request.body(),  # Read the request body
            cookies=request.cookies,
        )

        try:
            # Send the request to the React dev server
            resp = await async_client.send(
                fwd_request, stream=True, follow_redirects=False
            )

            # Prepare headers for the client response (filter excluded headers)
            # Also strip headers that can block iframe embedding inside IDEs/browsers
            excluded_headers = {
                "content-encoding",
                "content-length",  # StreamingResponse calculates this
                "transfer-encoding",
                "connection",
                "x-frame-options",
                "content-security-policy",
                "cross-origin-opener-policy",
                "cross-origin-embedder-policy",
                "cross-origin-resource-policy",
            }
            response_headers = {
                name: value
                for (name, value) in resp.headers.items()
                if name.lower() not in excluded_headers
            }

            # Use StreamingResponse to efficiently forward the content
            return StreamingResponse(
                content=resp.aiter_bytes(),  # Async iterator for the response body
                status_code=resp.status_code,
                headers=response_headers,
                media_type=resp.headers.get(
                    "content-type"
                ),  # Forward the original content type
            )

        except httpx.RequestError as e:
            # Handle errors connecting to the dev server (e.g., server not running)
            error_message = f"Proxy error: Unable to connect to React dev server at {REACT_DEV_SERVER_URL}. Error: {e}"
            print(f"[PROXY ERROR] {error_message}")  # Log the error
            return Response(content=error_message, status_code=502)  # Bad Gateway


REACT_BUILD_FOLDER = "/home/sahil/QUANTUM/network_simulator_project/simulator_1/ui/dist"


def serve_dist(app):
    # Serve main page
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        # If path is an API route, skip handling it here
        if path.startswith("api/"):
            return None
        print(os.path.join(REACT_BUILD_FOLDER, path))
        # If path exists as a file, serve it directly
        if path and os.path.exists(os.path.join(REACT_BUILD_FOLDER, path)):
            return send_from_directory(REACT_BUILD_FOLDER, path)

        # Otherwise return index.html for client-side routing
        return send_from_directory(REACT_BUILD_FOLDER, "index.html")

    # Optional: Explicitly handle assets folder
    @app.route("/assets/<path:path>")
    def serve_assets(path):
        return send_from_directory(os.path.join(REACT_BUILD_FOLDER, "assets"), path)


def register_blueprints(app: FastAPI):
    # Create the main router for the /api prefix
    api_router = APIRouter(
        prefix="/api", tags=["API Root"]  # Optional: Helps organize docs
    )
    
    try:
        config = get_config()
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
        config = None

    try:
        from server.api.topology.topology import topology_router
        api_router.include_router(topology_router)
    except Exception as e:
        print(f"Warning: Could not load topology router: {e}")

    try:
        from server.api.simulation.simulation import simulation_router
        api_router.include_router(simulation_router)
    except Exception as e:
        print(f"Warning: Could not load simulation router: {e}")

    try:
        from server.api.config.config_api import config_router
        api_router.include_router(config_router)
    except Exception as e:
        print(f"Warning: Could not load config router: {e}")

    if config and hasattr(config, 'control_config') and config.control_config.enable_ai_feature:
        try:
            from server.api.agent.agent import agent_router
            api_router.include_router(agent_router)
        except Exception as e:
            print(f"Warning: Could not load agent router: {e}")

    try:
        from server.api.conversation.conversation_api import conversation_router
        api_router.include_router(conversation_router)
    except Exception as e:
        print(f"Warning: Could not load conversation router: {e}")

    try:
        from server.api.user.user_api import user_router
        api_router.include_router(user_router)
    except Exception as e:
        print(f"Warning: Could not load user router: {e}")

    try:
        from server.api.quantum.quantum_api import quantum_router
        api_router.include_router(quantum_router)
    except Exception as e:
        print(f"Warning: Could not load quantum router: {e}")

    try:
        from server.student_status import router as student_status_router
        api_router.include_router(student_status_router)
    except Exception as e:
        print(f"Warning: Could not load student status router: {e}")

    @api_router.get("/{rest_of_path:path}")
    async def handle_404(rest_of_path: str):
        return Response(content="Route not found", status_code=404)

    app.include_router(api_router)


def register_routes(app: FastAPI):
    register_blueprints(app)
    if os.getenv("SERVE_DIST"):
        print("Serve UI Build")
        serve_dist(app)
    else:
        proxy_to_live_app(app)
