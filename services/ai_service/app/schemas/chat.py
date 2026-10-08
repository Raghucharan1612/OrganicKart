from pydantic import BaseModel, Field


class ChatSource(BaseModel):
    document: str
    title: str
    score: float | None = None
    url: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Customer message/question")


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
