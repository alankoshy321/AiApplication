## Simple Document QA (FastAPI + Weaviate + GPT4All)

### Setup (local)
1) Create a virtual env and install deps:
```
pip install -r requirements.txt
```
2) Start Weaviate and the app:
```
docker-compose up --build
```
3) Query:
```
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\":\"What stack does the demo use?\",\"mode\":\"baseline\"}"
```

### Endpoints
- `POST /ingest` — re-loads `data/sample_docs` into Weaviate.
- `POST /query` — body: `{ "question": "...", "k": 3, "mode": "baseline|hyde" }`.
- `GET /health` — readiness probe.

### Evaluation
- Baseline: `python evaluation/eval.py --mode baseline`
- HyDE: `python evaluation/eval.py --mode hyde`

### Notes
- GPT4All downloads the specified model on first use (default `ggml-gpt4all-j-v1.3-groovy`). Override with `GPT4ALL_MODEL`.
- Adjust embedding model via `EMBEDDING_MODEL`. Data folder defaults to `data/sample_docs`.



