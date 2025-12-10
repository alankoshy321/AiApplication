# Interactive Question-Answering Script for Document QA
# Usage: .\ask_question.ps1

param(
    [string]$Question = "",
    [string]$Mode = "baseline"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DOCUMENT QA - ASK QUESTIONS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if question provided as parameter
if ($Question -eq "") {
    Write-Host "Enter your question (or press Enter for examples):" -ForegroundColor Yellow
    $Question = Read-Host "Question"
    
    if ($Question -eq "") {
        Write-Host "`nUsing example questions...`n" -ForegroundColor Gray
        
        # Example questions
        $examples = @(
            "What is this application?",
            "How does ingestion work?",
            "What does HyDE do?",
            "How does the system retrieve documents?"
        )
        
        Write-Host "Example Questions:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $examples.Length; $i++) {
            Write-Host "  [$($i+1)] $($examples[$i])" -ForegroundColor White
        }
        Write-Host ""
        $choice = Read-Host "Select example (1-4) or type your own question"
        
        if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le 4) {
            $Question = $examples[[int]$choice - 1]
        } elseif ($choice -ne "") {
            $Question = $choice
        } else {
            $Question = $examples[0]
        }
    }
}

# Ask for mode if not provided
if ($Mode -eq "baseline") {
    Write-Host "`nSelect mode:" -ForegroundColor Yellow
    Write-Host "  [1] Baseline (standard retrieval)" -ForegroundColor White
    Write-Host "  [2] HyDE (enhanced retrieval)" -ForegroundColor White
    $modeChoice = Read-Host "`nMode (1 or 2, default: 1)"
    
    if ($modeChoice -eq "2") {
        $Mode = "hyde"
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PROCESSING YOUR QUESTION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Question: " -NoNewline -ForegroundColor Yellow
Write-Host $Question -ForegroundColor White
Write-Host "Mode: " -NoNewline -ForegroundColor Yellow
Write-Host $Mode -ForegroundColor White
Write-Host ""

# Check if API is available
Write-Host "[1/4] Checking API health..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "   ✓ API is running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API is not available. Is the app running?" -ForegroundColor Red
    Write-Host "   Start with: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Send query
Write-Host "[2/4] Sending query to API..." -ForegroundColor Cyan
$body = @{
    question = $Question
    mode = $Mode
} | ConvertTo-Json

try {
    Write-Host "[3/4] Retrieving documents and generating answer..." -ForegroundColor Cyan
    $result = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "[4/4] Processing complete!`n" -ForegroundColor Cyan
    
    # Display results
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ANSWER" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host $result.answer -ForegroundColor White
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  SOURCES ($($result.sources.Count) documents)" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    
    for ($i = 0; $i -lt $result.sources.Count; $i++) {
        $source = $result.sources[$i]
        Write-Host "`n[$($i+1)] " -NoNewline -ForegroundColor Yellow
        Write-Host "$($source.title) " -NoNewline -ForegroundColor Cyan
        Write-Host "($($source.source))" -ForegroundColor Gray
        
        # Show preview of content
        $preview = $source.content
        if ($preview.Length -gt 150) {
            $preview = $preview.Substring(0, 150) + "..."
        }
        Write-Host "   $preview" -ForegroundColor DarkGray
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  QUERY COMPLETE" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
}

# Ask if user wants to ask another question
Write-Host "Ask another question? (y/n): " -NoNewline -ForegroundColor Yellow
$again = Read-Host
if ($again -eq "y" -or $again -eq "Y") {
    & $PSCommandPath
}

