from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.rag.ingestion import ingest_customer_knowledge_base

app = FastAPI(
    title="OrganicKart AI Service",
    version="1.0.0",
    description="Role-based AI Assistant Microservice with RAG and Ollama LLM engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Ensure RAG knowledge base ingestion is initialized
ingest_customer_knowledge_base()


@app.get("/")
def root() -> dict:
    return {"service": settings.SERVICE_NAME, "status": "running"}


@app.get("/health")
def health() -> dict:
    return {
        "service": settings.SERVICE_NAME,
        "status": "healthy",
        "port": settings.SERVICE_PORT,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "mock_mode": settings.MOCK_LLM,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=False)
