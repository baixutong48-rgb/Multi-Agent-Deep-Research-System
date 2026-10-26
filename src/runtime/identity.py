from uuid import uuid4
from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeIdentity:
    run_id : str 
    thread_id : str
    session_id : str | None  = None
    user_id : str | None  = None

def create_runtime_identity(
    thread_id:str|None=None,
    session_id:str|None=None,
    user_id:str|None=None,
)->RuntimeIdentity:
    return RuntimeIdentity(
        run_id=_create_new_id('run_id'),
        thread_id=(thread_id if thread_id is not None else _create_new_id('thread_id')),
        session_id=session_id,
        user_id=user_id
    )

def _create_new_id(prefix:str)->str:
    return f'{prefix}_{uuid4().hex}'

