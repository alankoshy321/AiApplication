# Quick question script - simple one-liner style
# Usage: .\quick_ask.ps1 "Your question here"

param(
    [Parameter(Mandatory=$true)]
    [string]$Question,
    
    [string]$Mode = "baseline"
)

Write-Host "`nQuestion: $Question" -ForegroundColor Yellow
Write-Host "Mode: $Mode`n" -ForegroundColor Cyan

$body = @{
    question = $Question
    mode = $Mode
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "Answer:" -ForegroundColor Green
    Write-Host $result.answer -ForegroundColor White
    Write-Host "`nSources: $($result.sources.Count) documents found" -ForegroundColor Magenta
    
    if ($result.sources.Count -gt 0) {
        Write-Host "`nRetrieved Documents:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $result.sources.Count; $i++) {
            $source = $result.sources[$i]
            Write-Host "  [$($i+1)] $($source.title) ($($source.source))" -ForegroundColor Cyan
        }
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
