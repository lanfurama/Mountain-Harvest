"""Authentication middleware."""
import os
import base64
from starlette.responses import Response
from fasthtml.common import Beforeware


def basic_auth(req) -> bool:
    """Check basic authentication."""
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASSWORD")
    if not user or not pwd:
        return True
    auth = req.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        u, p = decoded.split(":", 1)
        return u == user and p == pwd
    except Exception:
        return False


def admin_before(req, auth=None):
    """Beforeware function for admin routes."""
    if not req.url.path.startswith("/admin"):
        return None
    if basic_auth(req):
        return None
    return Response(
        "Unauthorized",
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="Admin"'},
    )


admin_beforeware = Beforeware(admin_before)
