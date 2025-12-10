# How the Document QA Application Works

## 🎯 Quick Overview

This is a **Retrieval-Augmented Generation (RAG)** system that answers questions based on your documents.

## 📊 Architecture Flow

```
┌─────────────┐
│  Documents  │ (Text files in data/sample_docs/)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Ingestion     │ → Extract text → Create embeddings
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│  Weaviate   │ (Vector database storing embeddings)
│  Vector DB  │
└──────┬──────┘
       │
       │ Query Flow:
       │
┌──────▼──────────────────────────────────────┐
│  User Question                              │
└──────┬───────────────────────────────────────┘
       │
       ├─── Baseline Mode ────┐
       │                       │
       │   Embed Query         │
       │   Directly            │
       │                       │
       └─── HyDE Mode ─────────┘
                               │
                    Generate Hypothetical Answer
                               │
                    Embed Hypothetical Doc
                               │
       ┌───────────────────────┘
       │
       ▼
┌─────────────┐
│  Vector     │ → Find similar documents (top K)
│  Search     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieved  │ → Top 3 most relevant documents
│  Documents  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     LLM     │ → Generate answer from context
│  (MockLLM)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Answer    │ + Source documents
└─────────────┘
```

## 🔄 Step-by-Step Process

### 1. **Document Ingestion** (Happens at startup)
- Reads text files from `data/sample_docs/`
- Splits documents into chunks
- Converts text to vectors using `sentence-transformers/all-MiniLM-L6-v2`
- Stores vectors in Weaviate database

### 2. **Query Processing - Baseline Mode**
```
User Question
    ↓
Embed question directly
    ↓
Search Weaviate for similar vectors
    ↓
Retrieve top 3 documents
    ↓
LLM generates answer using retrieved context
```

### 3. **Query Processing - HyDE Mode** (Enhanced)
```
User Question
    ↓
Generate hypothetical answer document (using LLM)
    ↓
Embed the hypothetical document (not the question!)
    ↓
Search Weaviate for similar vectors
    ↓
Retrieve top 3 documents
    ↓
LLM generates final answer using retrieved context
```

**Why HyDE?** By generating a hypothetical answer first, we get a better embedding that matches the style/content of actual documents, improving retrieval accuracy.

## 🛠️ Components

| Component | Purpose |
|-----------|---------|
| **Weaviate** | Vector database storing document embeddings |
| **Sentence-Transformers** | Converts text to 384-dimensional vectors |
| **MockLLM** | Generates answers from retrieved context (simplified for demo) |
| **FastAPI** | REST API server handling requests |
| **HyDE** | Hypothetical Document Embeddings for improved retrieval |

## 📡 API Endpoints

### 1. Health Check
```bash
GET http://localhost:8000/health
```
Returns: `{"status": "ok"}`

### 2. Query Documents
```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "question": "Your question here",
  "mode": "baseline"  // or "hyde"
}
```

Returns:
```json
{
  "answer": "Generated answer...",
  "sources": [
    {
      "source": "filename.txt",
      "title": "title",
      "content": "Retrieved document content..."
    }
  ]
}
```

### 3. Ingest Documents
```bash
POST http://localhost:8000/ingest
```
Re-ingests documents from `data/sample_docs/`

## 🚀 How to Use

### Method 1: PowerShell
```powershell
$body = @{
    question = "What does ingestion do?"
    mode = "baseline"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:8000/query" `
    -Method POST -Body $body -ContentType "application/json"

Write-Host $result.answer
```

### Method 2: Browser (Interactive)
1. Open: http://localhost:8000/docs
2. Click on `POST /query`
3. Click "Try it out"
4. Enter your question and mode
5. Click "Execute"

### Method 3: curl
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"Your question","mode":"baseline"}'
```

## 🔍 Example Output

**Question:** "What does ingestion do?"

**Response:**
```json
{
  "answer": "Based on the retrieved documents, ingestion reads text files from the data directory and writes embeddings to Weaviate.",
  "sources": [
    {
      "source": "process.txt",
      "title": "process",
      "content": "Ingestion reads text files from the data directory and writes embeddings to Weaviate..."
    }
  ]
}
```

## 📈 Key Differences: Baseline vs HyDE

| Aspect | Baseline | HyDE |
|--------|----------|------|
| Query Embedding | Direct question embedding | Hypothetical document embedding |
| Retrieval Quality | Standard | Enhanced (better semantic matching) |
| Processing Time | Faster | Slightly slower (extra LLM call) |
| Use Case | General queries | Complex/ambiguous questions |

## 🎓 Learning Points

1. **Vector Search**: Documents are stored as vectors, allowing semantic similarity search
2. **Retrieval-Augmented Generation**: Answers are generated from retrieved context, not just LLM knowledge
3. **HyDE Enhancement**: Generating hypothetical documents improves retrieval by matching document style
4. **Local LLM**: Uses MockLLM for demonstration (can be replaced with GPT4All or other LLMs)

## 🔧 Current Status

- ✅ Weaviate running on port 8080
- ✅ FastAPI running on port 8000
- ✅ Documents ingested and searchable
- ✅ Baseline and HyDE modes working
- ✅ API endpoints functional

Visit **http://localhost:8000/docs** for interactive API testing!


