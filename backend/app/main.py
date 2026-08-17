from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes.styles import router as styles_router
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="ImageScribe API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def enforce_upload_size(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/api/describe":
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
                if int(content_length) > max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Uploaded file is too large for the configured request limit."},
                    )
            except (TypeError, ValueError):
                pass

    return await call_next(request)


from app.api.routes.describe import router as describe_router

app.include_router(styles_router)
app.include_router(describe_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
