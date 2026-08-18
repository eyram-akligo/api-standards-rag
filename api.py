import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from config import DB_CONNECTION_STRING, MODEL_NAME
from database import get_retriever
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from tools import retrieve_with_sources


app = FastAPI(
    title="API Standards RAG Agent",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class QuestionResponse(BaseModel):
    answer: str
    sources: str


def get_llm():
    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError("NVIDIA_API_KEY is not configured.")
    return ChatNVIDIA(model=MODEL_NAME)


@app.get("/health")
def health_check():
    try:
        engine = create_engine(DB_CONNECTION_STRING)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database is unavailable: {e}",
        ) from e


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    try:
        retriever = get_retriever()
        sources = retrieve_with_sources(retriever, request.question)

        if sources == "No relevant documents were found.":
            return QuestionResponse(
                answer="No relevant documents were found in the indexed API standards.",
                sources=sources,
            )

        llm = get_llm()
        prompt = f"""
Answer the question using only the retrieved API standards context below.

Question:
{request.question}

Retrieved context:
{sources}

Requirements:
-Do not invent requirements not present in the context.
-State clearly when the context is insufficient.
-Cite the source document and page number where possible.
"""
        response = llm.invoke(prompt)

        return QuestionResponse(
            answer=response.content,
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e