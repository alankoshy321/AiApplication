# How to Add Documents for Ingestion

## 📁 Where to Place Your Documents

### Default Location
Place your documents in: **`data/sample_docs/`**

### Supported File Formats
- ✅ **`.txt`** - Plain text files
- ✅ **`.pdf`** - PDF documents  
- ✅ **`.md`** - Markdown files

## 📂 Directory Structure

```
alproject/
├── data/
│   └── sample_docs/          ← PUT YOUR FILES HERE
│       ├── document1.txt
│       ├── report.pdf
│       ├── notes.md
│       └── your_file.pdf
├── app/
└── ...
```

## 🚀 How to Add Documents

### Method 1: Add Files to Default Location

1. **Copy your files** to `data/sample_docs/` folder
2. **Restart the application** or call the ingest endpoint:

```powershell
# Restart to auto-ingest
docker-compose restart app

# OR manually trigger ingestion
Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method POST
```

### Method 2: Use Custom Directory

1. **Set environment variable** in `docker-compose.yml`:
```yaml
environment:
  DATA_PATH: "data/your_custom_folder"
```

2. **Create the folder** and add your files
3. **Restart the application**

## 📄 Example: Adding a PDF

```powershell
# 1. Copy PDF to the data folder
Copy-Item "C:\path\to\your\document.pdf" -Destination "data\sample_docs\document.pdf"

# 2. Trigger ingestion
Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method POST

# 3. Verify it's ingested by querying
$body = @{
    question = "What is in the document?"
    mode = "baseline"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json"
```

## 🔄 Ingestion Process

When documents are ingested:

1. **Text Extraction**: 
   - `.txt` files: Read directly
   - `.pdf` files: Extract text from each page
   - `.md` files: Read as text

2. **Chunking**: Documents are split into manageable chunks

3. **Embedding**: Each chunk is converted to a vector using sentence-transformers

4. **Storage**: Vectors are stored in Weaviate for similarity search

## ✅ Verify Documents Are Ingested

```powershell
# Check health
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Query to see if documents are searchable
$body = @{
    question = "test"
    mode = "baseline"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json"
Write-Host "Found $($result.sources.Count) documents"
```

## 📝 Notes

- **File Size**: Large PDFs may take time to process
- **Text Quality**: PDFs with images/scans may have limited text extraction
- **Auto-Ingestion**: Documents in `data/sample_docs/` are automatically ingested on app startup
- **Re-ingestion**: Call `/ingest` endpoint to re-process all documents

## 🛠️ Troubleshooting

**PDFs not loading?**
- Ensure PyPDF2 is installed: `pip install PyPDF2`
- Check PDF is not password-protected
- Verify PDF contains extractable text (not just images)

**Documents not appearing?**
- Check file is in correct directory
- Verify file extension is supported (.txt, .pdf, .md)
- Check application logs: `docker-compose logs app`

**Need to change directory?**
- Update `DATA_PATH` in `docker-compose.yml` or `.env` file
- Restart containers: `docker-compose restart app`


