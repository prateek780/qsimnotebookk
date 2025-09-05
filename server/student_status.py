from fastapi import APIRouter
import importlib, json, os

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.get("/student-implementation-status/")
def student_impl_status():
    # Prefer plugin discovery (server mode)
    try:
        mod = importlib.import_module("student_plugin")
        if hasattr(mod, "StudentImplementation"):
            return {"student_implementation_ready": True, "source": "plugin"}
    except Exception:
        pass
    # Optional JSON fallback
    try:
        if os.path.exists("student_implementation_status.json"):
            with open("student_implementation_status.json", "r", encoding="utf-8") as f:
                payload = json.load(f)
            payload.setdefault("student_implementation_ready", True)
            payload.setdefault("source", "json")
            return payload
    except Exception:
        pass
    return {"student_implementation_ready": False, "source": "none"}