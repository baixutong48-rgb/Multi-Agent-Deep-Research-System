from pathlib import Path
from src.runtime.identity import RuntimeIdentity
from src.tools.files.workspace import Workspace

class WorkspaceFactory:
    def __init__(self,root:Path,max_read_bytes:int):
        self.root = root.resolve()
        self.max_read_bytes = max_read_bytes

    def create(self,identity:RuntimeIdentity)->Workspace:
        run_root = (self.root/identity.run_id)

        return Workspace(
            path=run_root,
            max_read_bytes=self.max_read_bytes
        )