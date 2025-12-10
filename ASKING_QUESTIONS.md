# How to Ask Questions - Command Reference

## 🚀 Quick Start

### Method 1: Quick Script (Recommended)
```powershell
.\quick_ask.ps1 "What does ingestion do?"
```

### Method 2: Interactive Script
```powershell
.\ask_question.ps1
```
This will prompt you for questions and show full results.

### Method 3: Direct PowerShell
```powershell
$q = @{question="Your question"; mode="baseline"} | ConvertTo-Json
$r = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $q -ContentType "application/json"
$r.answer
```

## 📋 Complete Examples

### Example 1: Simple Question (Baseline)
```powershell
.\quick_ask.ps1 "What is this application?"
```

**Output:**
```
Question: What is this application?
Mode: baseline

Answer:
Based on the retrieved documents, this appears to be a relevant answer to your question.

Sources: 3 documents found

Retrieved Documents:
  [1] process (process.txt)
  [2] process (process.txt)
  [3] process (process.txt)
```

### Example 2: Question with HyDE Mode
```powershell
.\quick_ask.ps1 "How does retrieval work?" -Mode hyde
```

### Example 3: Multiple Questions
```powershell
@("What is ingestion?", "How does HyDE work?") | ForEach-Object { .\quick_ask.ps1 $_ }
```

### Example 4: Interactive Mode
```powershell
.\ask_question.ps1
```
Then follow the prompts:
- Enter your question (or select from examples)
- Choose mode (baseline or hyde)
- View full results with sources

## 🎯 Command Options

### quick_ask.ps1 Parameters
- `-Question` (Required): Your question as a string
- `-Mode` (Optional): "baseline" or "hyde" (default: "baseline")

**Examples:**
```powershell
# Basic usage
.\quick_ask.ps1 "Your question"

# With HyDE mode
.\quick_ask.ps1 "Your question" -Mode hyde

# With baseline mode (explicit)
.\quick_ask.ps1 "Your question" -Mode baseline
```

## 📊 Output Format

All commands show:
1. **Question**: The question you asked
2. **Mode**: baseline or hyde
3. **Answer**: Generated answer from the LLM
4. **Sources**: Number of documents retrieved
5. **Retrieved Documents**: List of source documents with titles

## 🔧 Advanced Usage

### Using Variables
```powershell
$myQuestion = "What does the application do?"
.\quick_ask.ps1 $myQuestion
```

### Saving Results
```powershell
$q = @{question="Your question"; mode="baseline"} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $q -ContentType "application/json"

# Save answer
$result.answer | Out-File answer.txt

# Save full response
$result | ConvertTo-Json | Out-File full_response.json
```

### Batch Processing
```powershell
$questions = @(
    "What is ingestion?",
    "How does HyDE work?",
    "What is Weaviate?"
)

foreach ($q in $questions) {
    Write-Host "`n=== Processing: $q ===" -ForegroundColor Cyan
    .\quick_ask.ps1 $q
    Start-Sleep -Seconds 1
}
```

## 🌐 Browser Alternative

If you prefer a GUI:
1. Open: **http://localhost:8000/docs**
2. Click on `POST /query`
3. Click "Try it out"
4. Enter your question and mode
5. Click "Execute"

## 📝 Tips

1. **Be Specific**: More specific questions get better results
2. **Use HyDE**: For complex or ambiguous questions, use `-Mode hyde`
3. **Check Sources**: Always review the retrieved documents to verify accuracy
4. **Multiple Attempts**: Try rephrasing if you don't get good results

## ❓ Common Questions

**Q: The script says "API is not available"**
A: Start the application: `docker-compose up -d`

**Q: How do I see more details about sources?**
A: Use the interactive script: `.\ask_question.ps1`

**Q: Can I ask questions in a different language?**
A: Yes, but results depend on your document language and the embedding model

**Q: How do I change the number of documents retrieved?**
A: Modify the `k` parameter in the query (default is 3). You'll need to update the API call directly.

## 🎓 Example Session

```powershell
# Start interactive session
.\ask_question.ps1

# Or use quick commands
.\quick_ask.ps1 "What is this application?"
.\quick_ask.ps1 "How does ingestion work?" -Mode baseline
.\quick_ask.ps1 "Explain HyDE" -Mode hyde
```

---

**Ready to ask questions?** Run `.\quick_ask.ps1 "Your question"` to get started!

