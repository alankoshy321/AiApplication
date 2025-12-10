"""
Lightweight evaluation runner for the RAG pipeline.

Computes retrieval precision/recall and context precision/recall with ragas
for both baseline and HyDE-enhanced retrievers.
"""

from dataclasses import dataclass
from typing import Literal

import typer
from datasets import Dataset
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import GPT4All
from ragas import evaluate
from ragas.metrics import context_precision, context_recall, retrieval_precision, retrieval_recall

from app.config import get_settings
from app.ingest import ingest_documents, load_documents
from app.retriever import build_chain, build_hyde_embedder, build_vectorstore
from app.main import get_client


EvalMode = Literal["baseline", "hyde"]


@dataclass
class EvalResult:
    mode: EvalMode
    df: Dataset


def build_dataset(mode: EvalMode, k: int = 3) -> EvalResult:
    settings = get_settings()
    client = get_client(settings)
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    llm = GPT4All(model_name=settings.gpt4all_model, verbose=False)

    docs = load_documents(settings.data_path)
    ingest_documents(client, embeddings, settings.collection_name, docs)

    hyde_embedder = build_hyde_embedder(llm, embeddings) if mode == "hyde" else None
    vectorstore = build_vectorstore(client, settings, embeddings, hyde_embedder)
    chain = build_chain(vectorstore, llm, k=k)

    questions = [
        "What stack does the demo use?",
        "How does the system process a query?",
    ]
    ground_truths = [
        "It uses Weaviate for vectors and GPT4All as the local LLM.",
        "It embeds query text, retrieves similar chunks, and drafts an answer with the LLM.",
    ]

    records = []
    for q, gt in zip(questions, ground_truths):
        result = chain({"query": q})
        contexts = [doc.page_content for doc in result.get("source_documents", [])]
        records.append(
            {
                "question": q,
                "answer": result.get("result", ""),
                "contexts": contexts,
                "ground_truth": gt,
            }
        )

    ds = Dataset.from_list(records)
    return EvalResult(mode=mode, df=ds)


def run_eval(mode: EvalMode, k: int = 3):
    eval_result = build_dataset(mode, k=k)
    metrics = [retrieval_precision, retrieval_recall, context_precision, context_recall]
    scores = evaluate(dataset=eval_result.df, metrics=metrics)
    print(f"=== {mode.upper()} RESULTS ===")
    print(scores)


def main(
    mode: EvalMode = typer.Option("baseline", help="baseline or hyde"),
    k: int = typer.Option(3, help="top-k retrieval"),
):
    run_eval(mode, k)


if __name__ == "__main__":
    typer.run(main)

