import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger("ai-testgen")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()
        ip = request.client.host if request.client else "unknown"
        logger.info(f"REQ [{request_id}] {request.method} {request.url.path} | ip={ip}")
        try:
            response = await call_next(request)
            duration = round((time.time() - start) * 1000)
            logger.info(f"RES [{request_id}] {request.method} {request.url.path} | status={response.status_code} | {duration}ms")
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"ERR [{request_id}] {str(e)}")
            raise

def log_generation(framework, model, chunks, duration_ms):
    logger.info(f"GENERATE | framework={framework} | model={model} | chunks={chunks} | {duration_ms}ms")

def log_error(context, error):
    logger.error(f"ERROR | {context} | {error}")
