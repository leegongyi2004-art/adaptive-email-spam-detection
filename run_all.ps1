# Stop anything already running, then start both parts of the system.
#   1. the detection service (web console at http://127.0.0.1:8000)
#   2. the IMAP watcher (scores live mail and quarantines spam)
# Usage:  .\run_all.ps1

Write-Host "Stopping any running detection service or watcher ..." -ForegroundColor Yellow

# Kill anything still holding port 8000 (an orphaned uvicorn from a previous run).
$held = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
foreach ($c in $held) {
    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Kill any leftover uvicorn / imap_watch processes started from this project.
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'uvicorn|imap_watch' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

# Confirm the port really is free before starting again.
if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "Port 8000 is still in use. Close the program using it and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Starting the detection service in a new window ..." -ForegroundColor Green
Start-Process powershell -ArgumentList '-NoExit', '-Command',
    'cd C:\spam-project; .venv\Scripts\activate; uvicorn spam_detection.api:app'

Start-Sleep -Seconds 3

Write-Host "Console: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Starting the IMAP watcher in this window (Ctrl+C to stop) ..." -ForegroundColor Green

cd C:\spam-project
.venv\Scripts\activate
python -m spam_detection.imap_watch --all-folders --only-new --action quarantine --watch
