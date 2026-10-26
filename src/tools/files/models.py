from pydantic import BaseModel

class Artifact(BaseModel):
    name:str
    relative_path: str
    media_type: str
    size_bytes: int
