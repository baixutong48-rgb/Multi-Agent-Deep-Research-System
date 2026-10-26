from pathlib import Path
from src.tools.files.models import Artifact

class WorkspaceError(Exception):
    """Workspace 文件操作失败。"""

class FileAccessDeniedError(WorkspaceError):
    """文件访问超出了 Workspace 安全边界。"""

class FileTooLargeError(WorkspaceError):
    """文件超过允许读取的最大大小。"""

class Workspace:
    def __init__(self,path:Path,max_read_bytes: int = 5 * 1024 * 1024) -> None:
        self.root = path.resolve()
        self.input = self.root/'inputs'
        self.artifacts = self.root/'artifacts'
        self.max_read_bytes = max_read_bytes

        self.input.mkdir(parents=True,exist_ok=True)
        self.artifacts.mkdir(parents=True,exist_ok=True)

    async def read_inputs(self,filename:str)->str:
        path = self._check_safe_path(self.input,filename)
        if not path.exists():
            raise WorkspaceError(f'文件不存在{filename}')

        if not path.is_file():
            raise WorkspaceError(f'目标不是文件{filename}')

        size = path.stat().st_size()
        if size > self.max_read_bytes:
            raise FileTooLargeError(
                f"文件超过最大允许大小: {size} bytes"
            )
        try:
            return path.read_text(encoding='utf-8')
        
        except UnicodeDecodeError as exc:
            raise WorkspaceError(
                "当前文件不是可读取的 UTF-8 文本文件"
            ) from exc

        except OSError as exc:
            raise WorkspaceError(
                f"读取文件失败: {filename}"
            ) from exc

    async def write_artifact(self,filename:str,content:str,media_type:str)->Artifact:
        path = self._check_safe_path(self.artifacts,filename)
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')

        except OSError as exc:
            raise WorkspaceError(
                f"写入 Artifact 失败: {filename}"
            ) from exc

        return Artifact(name=path.name,relative_path=str(path.relative_to(self.root)),
                                media_type=media_type,size_bytes=path.stat().st_size)
    @staticmethod
    def _check_safe_path(base:Path,relative_path: str):
        candidate = (base/relative_path).resolve()
        try:
            candidate.relative_to(base.resolve())

        except ValueError as exc:
            raise FileAccessDeniedError("禁止访问 Workspace 之外的文件") from exc

        return candidate
        