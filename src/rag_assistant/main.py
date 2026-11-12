from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from rag_assistant.answering import answer_question
from rag_assistant.documents import chunk_text, extract_text
from rag_assistant.retrieval import add_document, document_list, search

app = FastAPI(title="RAG Knowledge Assistant", version="0.1.0")


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/documents", status_code=201)
async def upload_document(file: Annotated[UploadFile, File()]):
    try:
        data = await file.read(10 * 1024 * 1024 + 1)
        text = extract_text(file.filename or "", data)
        count = add_document(file.filename or "document", chunk_text(text))
        return {"filename": file.filename, "chunks_indexed": count}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Unable to process this document.") from exc


@app.get("/api/v1/documents")
def list_documents():
    return {"documents": document_list()}


@app.post("/api/v1/ask")
def ask(payload: Question):
    sources = search(payload.question, payload.top_k)
    return {
        "answer": answer_question(payload.question, sources),
        "sources": [
            {
                "citation": f"[Source {i}]",
                "filename": source["filename"],
                "chunk_index": source["chunk_index"],
                "excerpt": source["content"],
                "relevance": source["score"],
            }
            for i, source in enumerate(sources, 1)
        ],
    }
