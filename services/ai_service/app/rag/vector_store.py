import json
from pathlib import Path
from typing import Any

from app.rag.embeddings import LocalEmbeddingService


class LocalVectorStore:
    """
    Lightweight, persistent local vector store for OrganicKart RAG knowledge base.
    """

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self.embedding_service = LocalEmbeddingService()
        self.documents: list[dict[str, Any]] = []

    def fit_and_add_documents(self, docs: list[dict[str, Any]]) -> None:
        """
        Fits embedding vocabulary on document contents and generates document vectors.
        Each doc must contain: 'id', 'source', 'title', 'content'
        """
        contents = [d["content"] for d in docs]
        self.embedding_service.fit(contents)

        self.documents = []
        for doc in docs:
            vector = self.embedding_service.embed_text(doc["content"])
            self.documents.append({
                "id": doc.get("id", str(len(self.documents) + 1)),
                "source": doc.get("source", "unknown"),
                "title": doc.get("title", "Document Chunk"),
                "content": doc["content"],
                "vector": vector,
            })

    def similarity_search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Performs similarity search against query vector and returns top_k matching document chunks.
        """
        if not self.documents:
            return []

        query_vector = self.embedding_service.embed_text(query)
        scored_docs = []

        for doc in self.documents:
            doc_vec = doc.get("vector", [])
            score = LocalEmbeddingService.cosine_similarity(query_vector, doc_vec)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "score": float(score),
                "source": doc.get("source", ""),
                "title": doc.get("title", ""),
                "content": doc.get("content", ""),
            })
        return results

    def save(self, file_path: str | Path | None = None) -> None:
        path = Path(file_path) if file_path else self.storage_path
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "vocabulary": self.embedding_service.vocabulary,
            "idf": self.embedding_service._idf,
            "documents": self.documents,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, file_path: str | Path | None = None) -> bool:
        path = Path(file_path) if file_path else self.storage_path
        if not path or not path.exists():
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.embedding_service.vocabulary = data.get("vocabulary", [])
            self.embedding_service._idf = data.get("idf", {})
            self.documents = data.get("documents", [])
            return True
        except Exception:
            return False
