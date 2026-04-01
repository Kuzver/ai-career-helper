import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dishka.integrations.fastapi import setup_dishka
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from src.main.config import config
from src.presentation.fastapi.setup import setup_routes
from src.main.container import container


limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def normalize_cors(origins):
    if origins is None:
        return []
    if isinstance(origins, list):
        return origins
    if isinstance(origins, str):
        try:
            parsed = json.loads(origins)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [origins]
    return []


cors_origins = normalize_cors(config.api.cors)

app = FastAPI(title=config.api.project_name)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Слишком много запросов. Попробуйте позже."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-career-helper-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_routes(app, config)
setup_dishka(container, app)