import os

def answer_question(question: str, sources: list[dict]) -> str:
    if not sources:
        return "I couldn't find relevant information in the uploaded documents."
    if not os.getenv("OPENAI_API_KEY"):
        return "Relevant passages were found. Configure OPENAI_API_KEY to generate a synthesized answer; see the cited excerpts."
    from openai import OpenAI
    context = "\n\n".join(
        f"[Source {i}: {s['filename']}, chunk {s['chunk_index']}]\n{s['content']}"
        for i, s in enumerate(sources, 1))
    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), store=False,
        instructions=("Answer only from supplied excerpts. If evidence is insufficient, say so. "
                      "Cite claims inline using [Source N]. Never invent citations."),
        input=f"Question: {question}\n\nExcerpts:\n{context}")
    return response.output_text
