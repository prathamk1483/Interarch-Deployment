# --- Start of Script ---

Write-Host "`n=== Moving to Target Folder ===`n" -ForegroundColor Cyan
Set-Location "C:\Users\Pratham\Desktop\TestFolder"
Start-Sleep -Seconds 1
Write-Host "Current Directory: $((Get-Location).Path)" -ForegroundColor Yellow
Start-Sleep -Seconds 1

# --- Activate virtual environment ---
Write-Host "`n=== Activating virtual environment ===`n" -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"    # <-- change to .\venv if that's the actual name
Start-Sleep -Seconds 3

# --- Navigate to zrok folder ---
Write-Host "`n=== Enabling zrok (if not already) ===`n" -ForegroundColor Cyan
Set-Location ".\zrok"
Write-Host "Current Directory: $((Get-Location).Path)" -ForegroundColor Yellow
Start-Sleep -Seconds 1

# --- Disable + Enable Zrok ---
Write-Host "`n=== Disabling any previous zrok session ===`n" -ForegroundColor DarkYellow
& ".\zrok.exe" disable

Write-Host "`n=== Enabling zrok environment ===`n" -ForegroundColor Green
& ".\zrok.exe" enable aIkteI0aaJRX
Start-Sleep -Seconds 2

# --- Reserve public share ---
Write-Host "`n=== Reserving zrok public share ===`n" -ForegroundColor Yellow
& ".\zrok.exe" reserve public --backend-mode proxy --unique-name "interarch" http://localhost:8000
Start-Sleep -Seconds 5

# --- Start zrok tunnel (keep it foreground) ---
Write-Host "`n=== Starting zrok tunnel ===`n" -ForegroundColor Green
$zrokPath = (Join-Path (Get-Location) "zrok.exe")
Start-Process powershell -ArgumentList "-NoExit", "-Command `"$zrokPath share reserved 'interarch'`""
Start-Sleep -Seconds 3

# --- Move to Django project folder ---
Write-Host "`n=== Moving to Django project ===`n" -ForegroundColor Cyan
Set-Location "..\InterarchCMS"
Write-Host "Current Directory: $((Get-Location).Path)" -ForegroundColor Yellow
Start-Sleep -Seconds 2

# --- Start Django Server ---
Write-Host "`n=== Starting Django server on port 8000 ===`n" -ForegroundColor Green
python manage.py runserver
