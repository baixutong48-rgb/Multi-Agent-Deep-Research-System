from contextlib import contextmanager
from contextvars import ContextVar
from src.runtime.identity import RuntimeIdentity

class RuntimeContextError(RuntimeError):
    """当前执行环境不存在有效的 Runtime Context。"""

_runtime_context:ContextVar[RuntimeIdentity|None]=ContextVar("research_runtime_context",default=None)

def get_runtime_context()->RuntimeIdentity:
    context = _runtime_context.get()

    if context is None:
        raise RuntimeContextError("当前执行环境不存在有效的 Runtime Context。")

    return context

# def set_runtime_context(context:RuntimeIdentity)->Token[RuntimeIdentity|None]:
#     return _runtime_context.set(context)

# def reset_runtime_context(token:Token[RuntimeIdentity|None]):
#     _runtime_context.reset(token)
@contextmanager
def bind_runtime_context(context:RuntimeIdentity):
    token = _runtime_context.set(context)
    try:
        yield
    finally:
        _runtime_context.reset(token)