# PowerShell script to create a clean zip for PebblePad upload
# This creates a zip WITHOUT git history and with only one model

$projectName = "WeatherBot"
$zipName = "WeatherBot_Upload.zip"
$tempFolder = "WeatherBot_Clean"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Creating Clean WeatherBot Package for Upload" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Remove old temp folder if exists
if (Test-Path $tempFolder) {
    Write-Host "[1/6] Removing old temp folder..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $tempFolder
}

# Create temp folder
Write-Host "[2/6] Creating temporary clean copy..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $tempFolder | Out-Null

# Copy all files except excluded ones
Write-Host "[3/6] Copying project files..." -ForegroundColor Yellow
$excludeFolders = @('.git', '.rasa', '__pycache__', '.pytest_cache', 'results', 'logs')
$excludePattern = $excludeFolders -join '|'

Get-ChildItem -Path . -Recurse | Where-Object {
    $_.FullName -notmatch "($excludePattern)" -and 
    $_.FullName -notmatch "WeatherBot_Clean" -and
    $_.FullName -notmatch "\.zip$"
} | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\", "")
    $targetPath = Join-Path $tempFolder $relativePath
    
    if ($_.PSIsContainer) {
        if (-not (Test-Path $targetPath)) {
            New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        }
    } else {
        $targetDir = Split-Path $targetPath -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Copy-Item $_.FullName -Destination $targetPath -Force
    }
}

# Keep only latest model
Write-Host "[4/6] Keeping only the latest model..." -ForegroundColor Yellow
$modelFiles = Get-ChildItem -Path "$tempFolder\models\*.tar.gz" | Sort-Object LastWriteTime -Descending
if ($modelFiles.Count -gt 1) {
    $modelFiles | Select-Object -Skip 1 | Remove-Item -Force
    Write-Host "   Kept: $($modelFiles[0].Name)" -ForegroundColor Green
}

# Remove old zip if exists
if (Test-Path $zipName) {
    Write-Host "[5/6] Removing old zip file..." -ForegroundColor Yellow
    Remove-Item $zipName -Force
}

# Create zip file
Write-Host "[6/6] Creating zip archive..." -ForegroundColor Yellow
Compress-Archive -Path "$tempFolder\*" -DestinationPath $zipName -CompressionLevel Optimal

# Cleanup temp folder
Remove-Item -Recurse -Force $tempFolder

# Show results
$zipSize = (Get-Item $zipName).Length / 1MB
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Clean package created: $zipName" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "This package includes:" -ForegroundColor Yellow
Write-Host "  - Source code (actions, data, config)" -ForegroundColor White
Write-Host "  - Latest trained model only" -ForegroundColor White
Write-Host "  - Documentation and tests" -ForegroundColor White
Write-Host "  - Presentation and abstract" -ForegroundColor White
Write-Host "  - Deployment configs" -ForegroundColor White
Write-Host ""
Write-Host "Excluded for size:" -ForegroundColor Yellow
Write-Host "  - Git history (.git folder)" -ForegroundColor White
Write-Host "  - Old models (18 deleted)" -ForegroundColor White
Write-Host "  - Cache files (.rasa, __pycache__)" -ForegroundColor White
Write-Host ""
Write-Host "Ready to upload to PebblePad!" -ForegroundColor Green
Write-Host ""
