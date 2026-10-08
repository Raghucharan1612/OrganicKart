from pathlib import Path
from typing import Any

from app.config import settings
from app.rag.ingestion import ingest_customer_knowledge_base
from app.rag.vector_store import LocalVectorStore


class RAGRetriever:
    """
    Reusable retrieval engine for RAG knowledge retrieval.

    ``MIN_SCORE`` is the minimum cosine similarity a chunk must achieve before
    it is included in the context passed to the LLM.  Chunks below this
    threshold are excluded so that unrelated queries do not receive misleading
    context.
    """

    MIN_SCORE: float = 0.05

    def __init__(
        self,
        vector_store_path: str | Path | None = None,
        knowledge_base_dir: str | Path | None = None,
    ):
        path = Path(vector_store_path) if vector_store_path else Path(settings.VECTOR_STORE_PATH)
        self.vector_store = LocalVectorStore(path)
        if not self.vector_store.load():
            self.vector_store = ingest_customer_knowledge_base(
                kb_dir=knowledge_base_dir,
                output_vector_store_path=path,
            )

    def retrieve(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        top_k = top_k or settings.RAG_TOP_K
        results = self.vector_store.similarity_search(query, top_k=top_k)

        context_chunks = []
        sources = []
        seen_documents: set[str] = set()

        for item in results:
            score = item.get("score", 0.0)
            content = item.get("content", "")
            # Skip chunks that are below the relevance threshold
            if not content or score < self.MIN_SCORE:
                continue
            source_name = str(item.get("source", "unknown"))
            if source_name in seen_documents:
                continue
            seen_documents.add(source_name)
            if sum(len(chunk) for chunk in context_chunks) + len(content) > settings.RAG_MAX_CONTEXT_CHARS:
                break
            context_chunks.append(content)
            sources.append({
                "document": item.get("source", "unknown"),
                "title": item.get("title", "Reference"),
                "score": score,
            })

        context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else ""
        return {
            "context": context_text,
            "sources": sources,
            "raw_results": results,
        }
