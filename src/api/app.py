from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes.research import router as research_router
from src.api.websocket import router as websocket_router
from src.bootstrap import build_application_runtime

@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = await build_application_runtime()
    app.state.runtime = runtime
    try:
        yield
    finally:
        await runtime.shutdown()


    # 后续关闭：
    # database_service.close()
    # http clients
    # persistence pools

def create_app() -> FastAPI:
    app = FastAPI(title="Deep Research Agent",lifespan=lifespan,)
    app.include_router(
        research_router,
        prefix="/api/v1",
    )
    app.include_router(
        websocket_router,
        prefix="/api/v1",
    )
    return app

app = create_app()