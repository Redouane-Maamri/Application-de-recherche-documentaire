import ollama

from src.vector_store import search_chunks, get_collection

CHAT_MODEL = "qwen2.5:3b"


def answer_question(
    question: str,
    n_results: int = 3,
    source: str | None = None,
) -> dict:
    question = question.strip()

    if not question:
        raise ValueError("Please enter a question.")

    # Retrieve all chunks from the selected document when the user
    # asks for a complete inventory of its contents.
    exhaustive_terms = (
        "all ",
        "every ",
        "list all",
        "list every",
        "tous les",
        "toutes les",
        "chaque ",
    )
    exhaustive = any(term in question.lower() for term in exhaustive_terms)

    if exhaustive and source:
        collection = get_collection()
        data = collection.get(
            where={"source": source},
            include=["documents", "metadatas"],
        )

        passages = [
            {
                "text": data["documents"][i],
                "source": data["metadatas"][i]["source"],
                "page": data["metadatas"][i]["page"],
                "distance": 0,
            }
            for i in range(len(data["documents"]))
        ]
        passages.sort(key=lambda p: (p["page"], p["text"]))
    else:
        passages = search_chunks(
            question,
            n_results=n_results,
            source=source,
        )

    if not passages:
        return {
            "answer": "I couldn't find relevant information in the indexed documents.",
            "sources": [],
        }

    context_parts = []

    for passage in passages:
        context_parts.append(
            f"[Source: {passage['source']}, page {passage['page']}]\n"
            f"{passage['text']}"
        )

    context = "\n\n".join(context_parts)

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are DocuMind AI, a document research assistant. "
                    "Answer using only the provided document context. "
                    "Do not invent facts. If the context does not contain "
                    "the answer, say so clearly. Cite supporting information "
                    "using the exact source filename and page number, "
                    "for example [Source: resume.pdf, page 1]. "
                    "Answer in the language used by the question. "
                    "When asked to list all items, inspect every provided "
                    "passage and include every supported item. "
                    "Do not stop after finding only one or two examples."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"DOCUMENT CONTEXT:\n{context}\n\n"
                    f"QUESTION:\n{question}"
                ),
            },
        ],
        options={"num_ctx": 4096, "temperature": 0.1},
    )

    return {
        "answer": response.message.content,
        "sources": [
            {
                "source": p["source"],
                "page": p["page"],
                "text": p["text"],
            }
            for p in passages
        ],
    }
