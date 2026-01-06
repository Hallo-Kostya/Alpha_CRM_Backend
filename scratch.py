import json
import sys
import time
import uuid
import logging
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ----------------------------
# LOGGING SETUP (stdout, JSON)
# ----------------------------

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # дополнительные поля, если есть
        for field in (
            "request_id",
            "method",
            "path",
            "status",
            "duration_ms",
        ):
            if hasattr(record, field):
                log[field] = getattr(record, field)

        return json.dumps(log, ensure_ascii=False)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers.clear()
root_logger.addHandler(handler)

logger = logging.getLogger("app")


# ----------------------------
# FASTAPI APP
# ----------------------------

app = FastAPI()


@app.middleware("http")
async def http_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(
            "unhandled_exception",
            extra={"request_id": request_id},
        )
        raise

    duration_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "http_request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    response.headers["X-Request-ID"] = request_id
    return response


# ----------------------------
# DEMO ENDPOINTS
# ----------------------------

@app.get("/ok")
async def ok():
    logger.info("business_event", extra={"event": "ok_called"})
    return {"status": "ok"}


@app.get("/error")
async def error():
    raise RuntimeError("demo error")


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    logger.error(
        "runtime_error",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "internal error"},
    )

if __name__ == "__main__":
    uvicorn.run("scratch:app", host="0.0.0.0", port=8000, reload=True)