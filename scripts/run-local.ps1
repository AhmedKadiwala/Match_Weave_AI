# Double-click RUN_MATCHWEAVE.cmd. This one foreground server serves both the built UI and API.
param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$pythonPath = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host 'First launch: installing the project dependencies and building the UI.'
    & (Join-Path $PSScriptRoot 'setup.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'Setup failed. Inspect the output above.' }
}
if (-not (Test-Path -LiteralPath (Join-Path $repo 'frontend\dist\index.html'))) {
    Push-Location (Join-Path $repo 'frontend')
    try {
        if (-not (Test-Path -LiteralPath 'node_modules')) { npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' } }
        npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
}
$url = 'http://127.0.0.1:8000/'
try {
    $health = Invoke-RestMethod -Uri ($url + 'api/health') -TimeoutSec 2
    $page = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2
    if ($health.status -eq 'ok' -and $page.Content -match '<title>MatchWeave') {
        Write-Host "MatchWeave is already ready at $url"
        if (-not $NoBrowser) { [Diagnostics.Process]::Start($url) | Out-Null }
        exit 0
    }
} catch { }
if (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8000 is occupied by an older backend. Run scripts/stop.ps1, then double-click RUN_MATCHWEAVE.cmd again.'
}
Write-Host "Opening $url. Keep this window open while using the app. Press Ctrl+C to stop."
$launchArgs = @('-m', 'scripts.serve_local')
if ($NoBrowser) { $launchArgs += '--no-browser' }
& $pythonPath @launchArgs
if ($LASTEXITCODE -ne 0) { throw 'Server stopped with an error.' }
