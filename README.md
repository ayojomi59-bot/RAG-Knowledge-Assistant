# RAG Knowledge Assistant

A document-grounded question-answering API. Upload PDF, DOCX, TXT, or Markdown files, retrieve relevant passages, and generate answers with inline source citations.

## Features
- PDF, DOCX, TXT, and Markdown extraction
- Overlapping text chunking
- SQLite-backed chunk storage
- OpenAI embeddings with cosine-similarity retrieval when configured
- Offline lexical retrieval fallback
- OpenAI Responses API answer generation grounded in retrieved passages
- Source excerpts and citation metadata returned for inspection
- FastAPI, tests, Docker, and GitHub Actions CI

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn rag_assistant.main:app --reload
```
Visit http://127.0.0.1:8000/docs.

## Configuration
Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Export the variables in your shell or use your preferred environment manager. Without a key, lexical retrieval remains available; synthesized answers require the key.

- `OPENAI_MODEL`: answer model (default `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL`: embedding model (default `text-embedding-3-small`)
- `RAG_DB_PATH`: SQLite path (default `rag_assistant.db`)

Never commit API keys or confidential documents.

## API
- `GET /health` — health check
- `POST /api/v1/documents` — upload a file as multipart field `file` (10 MB max)
- `GET /api/v1/documents` — list indexed documents
- `POST /api/v1/ask` — retrieve passages and answer a question

Example request: `{"question":"What is the refund policy?","top_k":5}`

## Retrieval flow
1. Extract document text and split it into overlapping chunks.
2. Embed chunks and the query with OpenAI when configured.
3. Rank chunks by cosine similarity, or use lexical overlap offline.
4. Pass retrieved excerpts to the Responses API.
5. Return the answer alongside source identifiers and excerpts.

The lexical fallback is useful for local development but is not a substitute for evaluating semantic retrieval quality.

## Quality checks
```bash
ruff check .
pytest
```

## Security and limitations
Portfolio demonstration only. It does not yet include authentication, per-user document isolation, malware scanning, OCR for scanned PDFs, or document deletion. Do not upload sensitive documents to a public deployment.

## References
- [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- [OpenAI retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- [OpenAI Responses API](https://developers.openai.com/api/docs/guides/text)
