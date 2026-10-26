import json
from langchain_core.tools import tool,BaseTool
from src.tools.files.workspace import Workspace,WorkspaceError

def create_read_file_tool(workspace:Workspace)->BaseTool:

    @tool
    async def read_file(filename:str)->str:
        """
        读取当前研究任务中用户上传的文本文件。
        仅用于读取当前任务 Workspace 的 inputs 目录中的文件。
        当用户要求分析、总结或引用其上传的文本资料时使用。
        不允许访问当前任务之外的文件。
        """
        try:
            content = await workspace.read_inputs(filename)
            return json.dumps({
                'status':'seccess',
                'filename':filename,
                'content':content
            },ensure_ascii=False)

        except WorkspaceError as exc:

            return json.dumps(
                {
                    "status": "error",
                    "message": str(exc),
                },
                ensure_ascii=False,
            )

    return read_file

def create_write_markdown_file_tool(workspace:Workspace)->BaseTool:

    @tool
    async def write_markdown_file(filename:str,content:str)->str:
        """
        读取当前研究任务中用户上传的文本文件。
        仅用于读取当前任务 Workspace 的 inputs 目录中的文件。
        当用户要求分析、总结或引用其上传的文本资料时使用。
        不允许访问当前任务之外的文件。
        """
        if not filename.lower().endswith('md'):
            return json.dumps({
                "status": "error",
                "message": (
                "Markdown 报告文件必须使用 .md 扩展名"
                    ),
                },
                ensure_ascii=False,
            )
        try:
            artifact = await workspace.write_artifact(filename,content,media_type="text/markdown")
            return json.dumps({
                'status':'success',
                'artifact':artifact.model_dump()
            },ensure_ascii=False)

        except WorkspaceError as exc:

            return json.dumps(
                {
                    "status": "error",
                    "message": str(exc),
                },
                ensure_ascii=False,
            )
    return write_markdown_file
