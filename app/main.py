import logging
from typing import Any

import weaviate
from fastapi import Depends, FastAPI, HTTPException
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from weaviate.auth import AuthApiKey

from app.config import Settings, get_settings
from app.ingest import ingest_documents, load_documents
from app.retriever import (
    build_chain,
    build_hyde_embedder,
    build_llm,
    build_vectorstore,
)

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    question: str
    k: int = 3
    mode: str = "baseline"  # or "hyde"


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


def get_client(settings: Settings) -> weaviate.Client:
    auth = None
    if settings.weaviate_api_key:
        auth = AuthApiKey(settings.weaviate_api_key)
    return weaviate.Client(url=settings.weaviate_url, auth_client_secret=auth)


def get_embeddings(settings: Settings) -> Embeddings:
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def bootstrap(settings: Settings):
    client = get_client(settings)
    embeddings = get_embeddings(settings)
    llm = build_llm(settings)
    docs = load_documents(settings.data_path)
    if docs:
        ingest_documents(client, embeddings, settings.collection_name, docs)
        logger.info("Ingested %s documents", len(docs))
    else:
        logger.warning("No documents found to ingest at %s", settings.data_path)
    return client, embeddings, llm


def create_app() -> FastAPI:
    app = FastAPI(title="Simple Doc QA with Weaviate + FastAPI")
    settings = get_settings()
    client, embeddings, llm = bootstrap(settings)

    base_chain = build_chain(client, settings.collection_name, embeddings, llm)

    hyde_embedder = build_hyde_embedder(llm, embeddings)
    hyde_chain = build_chain(client, settings.collection_name, hyde_embedder, llm)

    @app.post("/query", response_model=QueryResponse)
    def query(req: QueryRequest, settings: Settings = Depends(get_settings)):
        chain = base_chain if req.mode == "baseline" else hyde_chain
        try:
            result = chain({"query": req.question})
        except Exception as exc:  # pragma: no cover - runtime safety
            logger.exception("Query failed")
            raise HTTPException(status_code=500, detail=str(exc))
        sources = []
        for doc in result.get("source_documents", []):
            sources.append(
                {
                    "source": doc.metadata.get("source"),
                    "title": doc.metadata.get("title"),
                    "content": doc.page_content,
                }
            )
        return QueryResponse(answer=result.get("result", ""), sources=sources)

    @app.post("/ingest")
    def ingest(settings: Settings = Depends(get_settings)):
        docs = load_documents(settings.data_path)
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found to ingest")
        count = ingest_documents(client, embeddings, settings.collection_name, docs)
        return {"ingested": count}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

