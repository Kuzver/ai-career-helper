from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from src.main.config import config
from src.presentation.fastapi.setup import setup_routes
from fastapi.middleware.cors import CORSMiddleware
from src.main.container import container

app = FastAPI(
    title=config.api.project_name
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_routes(app, config)
setup_dishka(container, app)
