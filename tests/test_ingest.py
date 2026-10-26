import pytest

from src.ingest import chunk_text


def test_chunk_text_returns_content():
    chunks = chunk_text("DocuMind AI is a document assistant.")

    assert len(chunks) == 1
    assert chunks[0] == "DocuMind AI is a document assistant."


def test_chunk_text_splits_long_text():
    text = "A" * 2500

    chunks = chunk_text(text, chunk_size=1000, overlap=150)

    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_chunk_text_preserves_overlap():
    text = "A" * 2500

    chunks = chunk_text(text, chunk_size=1000, overlap=150)

    assert chunks[0][-150:] == chunks[1][:150]


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("Some text", chunk_size=100, overlap=100)


def test_chunk_text_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Some text", chunk_size=0)
