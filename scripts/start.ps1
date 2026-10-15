$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$runtime = Join-Path $repo 'runtime'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$owned = @()
if (-not (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    $pythonPath = Join-Path $repo '.venv\Scripts\python.exe'
    $backendProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000' -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'backend.log') -RedirectStandardError (Join-Path $runtime 'backend-errors.log')
    $owned += @{ id=$backendProcess.Id; kind='backend'; started=$backendProcess.StartTime.ToUniversalTime().ToString('O') }
}
if (-not (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue)) {
    $viteScript = Join-Path $repo 'frontend\node_modules\vite\bin\vite.js'
    $viteArguments = '"' + $viteScript + '" --host 127.0.0.1 --port 5173'
    $frontendProcess = Start-Process -FilePath 'node.exe' -ArgumentList $viteArguments -WorkingDirectory (Join-Path $repo 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'frontend.log') -RedirectStandardError (Join-Path $runtime 'frontend-errors.log')
    $owned += @{ id=$frontendProcess.Id; kind='frontend'; started=$frontendProcess.StartTime.ToUniversalTime().ToString('O') }
}
if ($owned.Count -gt 0) { ConvertTo-Json -InputObject @($owned) | Set-Content -Encoding utf8 (Join-Path $runtime 'owned-processes.json') }
$ready = $false
$deadline = [DateTime]::UtcNow.AddSeconds(45)
while ([DateTime]::UtcNow -lt $deadline) {
    try {
        $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2
        $frontend = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5173' -TimeoutSec 2
        if ($health.status -eq 'ok' -and $frontend.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $ready) { throw 'Servers did not become ready within 45 seconds. Inspect runtime/backend-errors.log and runtime/frontend-errors.log.' }
Write-Host 'MatchWeave: http://127.0.0.1:5173'
Write-Host 'API documentation: http://127.0.0.1:8000/docs'
Write-Host 'The static replay works immediately. Click Connect local backend for fresh workflows.'
Write-Host 'Optional local AI: .\.venv\Scripts\python.exe -m scripts.local_model'
