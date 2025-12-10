# Simple test script for the Document QA API

Write-Host "`n=== Document QA API Test Script ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "   ✓ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Error: $_" -ForegroundColor Red
}

# Test 2: Baseline Query
Write-Host "`n2. Testing Baseline Query..." -ForegroundColor Yellow
$query1 = @{
    question = "What is this application?"
    mode = "baseline"
} | ConvertTo-Json

try {
    $result1 = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $query1 -ContentType "application/json"
    Write-Host "   Question: $($query1 | ConvertFrom-Json | Select-Object -ExpandProperty question)" -ForegroundColor White
    Write-Host "   Answer: $($result1.answer)" -ForegroundColor Green
    Write-Host "   Sources found: $($result1.sources.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ✗ Error: $_" -ForegroundColor Red
}

# Test 3: HyDE Query
Write-Host "`n3. Testing HyDE Query..." -ForegroundColor Yellow
$query2 = @{
    question = "How does the system retrieve documents?"
    mode = "hyde"
} | ConvertTo-Json

try {
    $result2 = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $query2 -ContentType "application/json"
    Write-Host "   Question: $($query2 | ConvertFrom-Json | Select-Object -ExpandProperty question)" -ForegroundColor White
    Write-Host "   Answer: $($result2.answer)" -ForegroundColor Green
    Write-Host "   Sources found: $($result2.sources.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ✗ Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "`nTip: Visit http://localhost:8000/docs for interactive API documentation" -ForegroundColor Yellow


