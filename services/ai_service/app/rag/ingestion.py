from pathlib import Path
from typing import Any

from app.config import settings
from app.rag.vector_store import LocalVectorStore


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Split a Markdown document into content-rich chunks.

    Key invariant: a paragraph that is *only* a Markdown heading (``# ...``)
    is never emitted as a standalone chunk — it is always merged forward into
    the next paragraph.  This prevents bare title lines from outranking actual
    content chunks in TF-IDF similarity search.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []

    # Carry-forward buffer for heading-only paragraphs
    heading_prefix = ""
    current_chunk = ""

    for para in paragraphs:
        # Detect a heading-only paragraph (every non-empty line starts with #)
        lines = [ln for ln in para.splitlines() if ln.strip()]
        is_heading_only = lines and all(ln.lstrip().startswith("#") for ln in lines)

        if is_heading_only:
            # Don't emit as a chunk on its own — carry it forward as a prefix
            # to the next paragraph so it provides context but not a retrieval
            # signal by itself.
            heading_prefix = (heading_prefix + "\n\n" + para).strip() if heading_prefix else para
            continue

        # Prepend any carried-forward heading to the current paragraph
        effective_para = (heading_prefix + "\n\n" + para).strip() if heading_prefix else para
        heading_prefix = ""  # consumed

        if len(current_chunk) + len(effective_para) + 2 <= chunk_size:
            current_chunk = (current_chunk + "\n\n" + effective_para).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = effective_para

    # Flush remainder — any trailing heading-only content joins the last chunk
    if heading_prefix:
        current_chunk = (current_chunk + "\n\n" + heading_prefix).strip() if current_chunk else heading_prefix
    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [text]


def ingest_customer_knowledge_base(
    kb_dir: str | Path | None = None,
    output_vector_store_path: str | Path | None = None,
) -> LocalVectorStore:
    dir_path = Path(kb_dir) if kb_dir else Path(settings.KNOWLEDGE_BASE_DIR) / "customer"
    store_path = Path(output_vector_store_path) if output_vector_store_path else Path(settings.VECTOR_STORE_PATH)

    docs: list[dict[str, Any]] = []

    if dir_path.exists():
        for file_path in dir_path.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                title = file_path.stem.replace("_", " ").title()
                chunks = chunk_text(content)
                for idx, chunk in enumerate(chunks):
                    docs.append({
                        "id": f"{file_path.name}_{idx+1}",
                        "source": file_path.name,
                        "title": title,
                        "content": chunk,
                    })
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")

    vector_store = LocalVectorStore(store_path)
    if docs:
        vector_store.fit_and_add_documents(docs)
        vector_store.save()
    else:
        # Fallback if no files loaded
        vector_store.load()

    return vector_store


if __name__ == "__main__":
    store = ingest_customer_knowledge_base()
    print(f"Ingested {len(store.documents)} chunks into vector store.")
