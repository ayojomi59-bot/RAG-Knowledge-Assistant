import pytest

from rag_assistant.documents import chunk_text, extract_text


def test_extract_and_chunk_text():
    text = extract_text("notes.txt", b"retrieval augmented generation " * 80)
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    assert all(chunks)


def test_reject_unsupported():
    with pytest.raises(ValueError, match="Only PDF"):
        extract_text("photo.png", b"data")
