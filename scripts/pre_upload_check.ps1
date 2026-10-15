$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$required = @('render.yaml','requirements-render.txt','frontend\vercel.json','GOOGLE_KEEP_ALIVE.gs','models\historical-result-evaluation.json','models\historical-result-model.json','frontend\public\history\summary.json','frontend\public\artifacts\index.json')
foreach ($file in $required) { if (-not (Test-Path -LiteralPath $file)) { throw "Missing required upload file: $file" } }
& '.\.venv\Scripts\python.exe' -m pytest -q --junitxml=docs/reports/backend-tests.xml
if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
node --test scripts/tests/keep-alive.test.cjs
if ($LASTEXITCODE -ne 0) { throw 'Google ping unit checks failed.' }
Push-Location frontend
try { npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' } } finally { Pop-Location }
Write-Host 'Local pre-upload checks passed. Read UPLOAD_CHECKLIST.md for account setup and live deployment checks.'
Write-Host 'This does not claim that Vercel, Render or your Google trigger is already deployed.'
