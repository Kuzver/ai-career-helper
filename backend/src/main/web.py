from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dishka.integrations.fastapi import setup_dishka
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.main.config import config
from src.presentation.fastapi.setup import setup_routes
from fastapi.middleware.cors import CORSMiddleware
from src.main.container import container

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title=config.api.project_name
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Слишком много запросов. Попробуйте позже."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_routes(app, config)
setup_dishka(container, app)
