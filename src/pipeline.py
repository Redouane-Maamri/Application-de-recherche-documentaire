from pathlib import Path

from src.ingest import extract_pages, chunk_text
from src.vector_store import store_chunks


def ingest_pdf(pdf_path: str) -> int:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    pages = extract_pages(str(path))
    chunks_to_store = []

    for page in pages:
        chunks = chunk_text(page["text"])

        for chunk_index, chunk in enumerate(chunks):
            chunks_to_store.append({
                "source": page["source"],
                "page": page["page"],
                "chunk_index": chunk_index,
                "text": chunk,
            })

    if not chunks_to_store:
        raise ValueError(
            "No extractable text found. The PDF may be scanned or empty."
        )

    return store_chunks(chunks_to_store)
