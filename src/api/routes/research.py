from fastapi import Depends,APIRouter,status,HTTPException
import asyncio
from src.api.dependencies import (ApplicationRuntime,get_runtime,)
from src.api.schemas import (ResearchCreatedResponse,ResearchRequest,ResearchStatusResponse)
from src.runtime.identity import create_runtime_identity

router = APIRouter(prefix='/research',tags=['research'])

@router.post("",response_model=ResearchCreatedResponse,status_code=status.HTTP_202_ACCEPTED)
async def create_research(request:ResearchRequest,runtime:ApplicationRuntime = Depends(get_runtime))->ResearchCreatedResponse:
    identity = create_runtime_identity()
    run = await runtime.runner.create_run(identity=identity,query=request.query)
    runtime.tasks.start(identity.run_id,runtime.runner.execute(identity=identity,query=request.query))
    return ResearchCreatedResponse(run_id=run.run_id,status=run.status)

@router.get("/{run_id}",response_model=ResearchStatusResponse,)
async def get_research(run_id: str,runtime: ApplicationRuntime = Depends(get_runtime),) -> ResearchStatusResponse:

    run = await runtime.run_store.get(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Research Run 不存在",
        )

    return ResearchStatusResponse(
        run_id=run.run_id,
        status=run.status,
        result=run.result,
        error=run.error,
    )