from pydantic import BaseModel,Field

class KnowledgeDocument(BaseModel):
    content:str
    source:str|None=None
    title:str|None=None
    score:float|None=None
    metadata:dict[str,object]=Field(
        default_factory=dict
    )

class KnowledgeSearchResult(BaseModel):
    query:str
    document:KnowledgeDocument=Field(
        default_factory=list
    )