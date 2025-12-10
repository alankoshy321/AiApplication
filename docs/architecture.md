## Architecture

```mermaid
flowchart LR
    subgraph User
        Q[Query]
    end
    Q --> API[FastAPI /query]
    API -->|embeddings| V[Weaviate Vector Store]
    API -->|LLM| L[GPT4All (local)]
    V --> API
    subgraph Data
        D1[data/sample_docs]
    end
    D1 -->|ingest| V
```

### Data Flow
- Ingestion loads `data/sample_docs`, embeds with `sentence-transformers/all-MiniLM-L6-v2`, and stores vectors in Weaviate.
- Queries hit `POST /query` on FastAPI, which retrieves similar documents from Weaviate.
- The GPT4All local LLM generates the final answer using retrieved context.
- HyDE mode generates a hypothetical passage to improve query embeddings before retrieval.

### Evaluation Summary
- Run `python evaluation/eval.py --mode baseline` for the base pipeline.
- Run `python evaluation/eval.py --mode hyde` to measure HyDE-enhanced retrieval.
- Metrics reported via Ragas: retrieval precision/recall and context precision/recall.



