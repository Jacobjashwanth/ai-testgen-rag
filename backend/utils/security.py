import time
import re
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_rate_store = defaultdict(list)
RATE_LIMIT = 30
RATE_WINDOW = 60

def check_rate_limit(ip):
    now = time.time()
    _rate_store[ip] = [t for t in _rate_store[ip] if t > now - RATE_WINDOW]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return False
    _rate_store[ip].append(now)
    return True

def sanitize_prompt(prompt):
    if len(prompt) > 2000:
        raise ValueError("Prompt too long — max 2000 characters")
    banned = ["ignore previous instructions", "jailbreak", "act as", "you are now"]
    lower = prompt.lower()
    for b in banned:
        if b in lower:
            raise ValueError("Prompt contains disallowed content")
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", prompt).strip()

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ip = request.client.host if request.client else "unknown"
        if request.url.path in ["/generate-tests", "/upload"]:
            if not check_rate_limit(ip):
                return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded — max 30 requests/min"})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
