import streamlit as st
from pathlib import Path

from src.pipeline import ingest_pdf
from src.rag import answer_question
from src.vector_store import list_sources

st.set_page_config(page_title="DocuMind AI", page_icon="📚")
st.title("📚 DocuMind AI")
st.caption("Local AI document assistant")

with st.sidebar:
    st.header("Your documents")
    files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True,
    )

    if st.button("Index documents"):
        if not files:
            st.warning("Upload a PDF first.")
        else:
            for file in files:
                try:
                    path = Path("data/documents") / Path(file.name).name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(file.getvalue())
                    count = ingest_pdf(str(path))
                    st.success(f"{file.name}: indexed {count} chunks")
                except Exception as exc:
                    st.error(f"Indexing failed: {exc}")

    st.divider()
    st.subheader("Search settings")

    sources = list_sources()
    choices = ["All documents"] + sources

    selected_source = st.selectbox(
        "Search in",
        choices,
        help="Choose one PDF to restrict answers to that document.",
    )

    source_filter = (
        selected_source
        if selected_source != "All documents"
        else None
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            st.caption(f"{source['source']} — page {source['page']}")

question = st.chat_input("Ask about your documents...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching and thinking..."):
                result = answer_question(
                    question,
                    source=source_filter,
                )

            st.markdown(result["answer"])

            for source in result["sources"]:
                st.caption(f"{source['source']} — page {source['page']}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
            })

        except Exception as exc:
            st.error(f"Error: {exc}")
