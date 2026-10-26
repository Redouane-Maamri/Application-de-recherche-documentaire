import chromadb
import ollama

from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "chroma_db"
EMBED_MODEL = "nomic-embed-text"
COLLECTION_NAME = "documind_documents"


def get_collection():
    """Open or create the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(DB_PATH))
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate local embeddings using Ollama."""
    if not texts:
        return []

    response = ollama.embed(
        model=EMBED_MODEL,
        input=texts,
    )
    return response["embeddings"]


def list_sources() -> list[str]:
    """Return the unique filenames currently indexed."""
    collection = get_collection()

    data = collection.get(include=["metadatas"])

    return sorted({
        metadata["source"]
        for metadata in data["metadatas"]
        if metadata and metadata.get("source")
    })


def store_chunks(chunks: list[dict]) -> int:
    """Replace previously indexed chunks for each source."""
    if not chunks:
        return 0

    collection = get_collection()
    texts = [item["text"] for item in chunks]
    embeddings = embed_texts(texts)

    ids = [
        f"{item['source']}-page{item['page']}-chunk{item['chunk_index']}"
        for item in chunks
    ]

    metadatas = [
        {
            "source": item["source"],
            "page": item["page"],
            "chunk_index": item["chunk_index"],
        }
        for item in chunks
    ]

    # Remove old chunks only after embeddings have been generated.
    sources = {item["source"] for item in chunks}
    for source in sources:
        collection.delete(where={"source": source})

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def search_chunks(
    question: str,
    n_results: int = 4,
    source: str | None = None,
) -> list[dict]:
    """Retrieve relevant passages, optionally from one PDF only."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    embedding = embed_texts([question])[0]

    query_args = {
        "query_embeddings": [embedding],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }

    if source:
        query_args["where"] = {"source": source}

    results = collection.query(**query_args)

    passages = []

    for i, text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        passages.append({
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": results["distances"][0][i],
        })

    return passages
