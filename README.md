# DocuMind AI

### Local Intelligent Document Research Assistant

DocuMind AI is a document intelligence application designed to help users organize, classify, search and understand PDF documents using Machine Learning and Retrieval-Augmented Generation (RAG).

The application combines document classification with semantic retrieval and local Large Language Model inference to provide contextual answers grounded in uploaded documents.

## Project Objectives

- Automatically extract and process text from PDF documents.
- Classify documents into predefined categories using Machine Learning.
- Generate semantic embeddings and index document chunks.
- Retrieve relevant passages based on user questions.
- Generate contextual answers with document and page references.
- Run AI inference locally without relying on paid external AI APIs.

## Core Features

### 1. Document Processing
- PDF text extraction.
- Text cleaning and chunking.
- Document ingestion pipeline.

### 2. Document Classification
- TF-IDF feature extraction.
- Logistic Regression classification.
- Document categories: Academic, Technical, Business, Administrative and Legal.

### 3. Retrieval-Augmented Generation
- Local embeddings using Nomic Embed Text.
- Vector storage and semantic retrieval with ChromaDB.
- Answer generation using Qwen 2.5 3B through Ollama.
- Source-grounded answers with document references.

### 4. User Interface
- PDF upload.
- Document interaction.
- Question answering through a Streamlit application.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Machine Learning | Scikit-learn |
| Text extraction | PyPDF |
| Embeddings | Nomic Embed Text |
| Vector database | ChromaDB |
| Local LLM | Qwen 2.5 3B |
| Model runtime | Ollama |
| User interface | Streamlit |
| Testing | Pytest |

FastAPI, automated CI and additional quality controls are planned development milestones.

## Project Architecture

The application is organized around two complementary processing components:

- **Document Classification:** predicts the category of an uploaded document.
- **RAG Pipeline:** retrieves relevant document passages and generates answers grounded in their content.

Both components contribute to the document research workflow.

## Team Members

| Member | GitHub | Responsibility |
|---|---|---|
| Redouane Maamri | [@redouanemaamri](https://github.com/redouanemaamri) | AI and Backend Engineering |
| Mouad Sekoumi | [@mouadsekkoumi](https://github.com/mouadsekkoumi) | Evaluation and Application Engineering |

## Project Information

- **Project:** DocuMind AI
- **Institution:** EMSI
- **Project duration:** 3 weeks
- **Project type:** Machine Learning and Retrieval-Augmented Generation

**Catalogue number:** To be completed according to the official project catalogue.

## Development Status

The initial PDF ingestion, local RAG pipeline, Streamlit interface and document classification components have been developed.

The project is being progressively improved through a structured three-week development plan covering API development, evaluation, testing, continuous integration and documentation.

## License

Academic project developed for educational purposes.
