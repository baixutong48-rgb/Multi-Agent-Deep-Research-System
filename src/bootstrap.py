from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

from src.agents.factory import ResearchAgentFactory
from src.agents.subagents.factory import (
    ResearchToolSet,
    create_research_subagents,
)
from src.api.dependencies import ApplicationRuntime
from src.core.config import get_setting
from src.llm.factory import create_llm

from src.observability.store import InMemoryTraceStore
from src.observability.tracer import ResearchTracer

from src.runtime.runner import ResearchRunner
from src.runtime.store import InMemoryRunStore
from src.runtime.tasks import TaskRegistry
from src.runtime.workspace import WorkspaceFactory

from src.tools.database.service import DatabaseService
from src.tools.database.tools import (
    create_database_query_tool,
    create_database_schema_tool,
)
from src.tools.knowledge.client import HTTPKnowledgeClient
from src.tools.knowledge.tools import create_knowledge_tool
from src.tools.search.client import TavilySearchClient
from src.tools.search.tools import create_search_tool

async def build_application_runtime() -> ApplicationRuntime:
    settings = get_setting()
    # 1. LLM
    model = create_llm()
    # 2. Application-scoped infrastructure
    search_client = TavilySearchClient(
        api_key=settings.tavily.api_key,
        timeout=settings.tavily.timeout,
    )
    database_service = DatabaseService(
        database_url=settings.database.url,
        query_timeout=settings.database.query_timeout,
        max_rows=settings.database.max_rows,
    )
    knowledge_client = HTTPKnowledgeClient(
        base_url=settings.knowledge.base_url,
        api_key=settings.knowledge.api_key,
        timeout=settings.knowledge.timeout,
    )
    # 3. Research tools
    web_search_tool = create_search_tool(search_client)
    database_schema_tool = create_database_schema_tool(database_service)
    database_query_tool = create_database_query_tool(database_service)
    knowledge_tool = create_knowledge_tool(knowledge_client)
    # 4. SubAgents
    research_tools = ResearchToolSet(
        web_search=web_search_tool,
        database_schema=database_schema_tool,
        database_query=database_query_tool,
        knowledge_search=knowledge_tool,
    )
    subagents = create_research_subagents(research_tools)
    # 5. Checkpointer
    checkpointer = InMemorySaver()
    # 6. Main Agent Factory
    agent_factory = ResearchAgentFactory(
        model=model,
        subagents=subagents,
        checkpointer=checkpointer,
    )
    # 7. Workspace Factory
    workspace_factory = WorkspaceFactory(
        root=Path(settings.workspace.root),
        max_read_bytes=settings.workspace.max_read_bytes,
    )
    # 8. Observability
    trace_store = InMemoryTraceStore()

    tracer = ResearchTracer(store=trace_store)
    # 9. Runtime state
    run_store = InMemoryRunStore()

    runner = ResearchRunner(
        agent_factory=agent_factory,
        workspace_factory=workspace_factory,
        run_store=run_store,
        tracer=tracer,
    )

    tasks = TaskRegistry()

    # 10. FastAPI runtime
    return ApplicationRuntime(
        runner=runner,
        run_store=run_store,
        tasks=tasks,
        db_service=database_service,
        search_client=search_client
    )