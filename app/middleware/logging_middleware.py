import time
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """
    Middleware untuk logging semua HTTP requests
    - Log incoming request
    - Log response dengan status code dan duration
    - Handle dan log exceptions
    """
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host}"
    )

    try:
        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Log response berdasarkan status code
        if response.status_code < 400:
            logger.info(
                f"✅ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        else:
            logger.warning(
                f"⚠️ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Duration: {duration:.3f}s",
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(e),
                "path": request.url.path,
                "method": request.method,
                "timestamp": datetime.now().isoformat()
            }
        )
