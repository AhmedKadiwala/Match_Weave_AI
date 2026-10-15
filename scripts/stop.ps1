$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$record = Join-Path $repo 'runtime\owned-processes.json'
if (-not (Test-Path -LiteralPath $record)) { Write-Host 'No script-owned processes recorded.'; exit }
$records = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($record))
foreach ($entry in $records) {
    $ownedProcess = Get-Process -Id ([int]$entry.id) -ErrorAction SilentlyContinue
    if (-not $ownedProcess) { continue }
    $recordedStart = [DateTime]::Parse([string]$entry.started).ToUniversalTime()
    if ($ownedProcess.StartTime.ToUniversalTime().Ticks -ne $recordedStart.Ticks) { continue }
    $children = Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $ownedProcess.Id
    foreach ($child in $children) {
        $grandchildren = Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $child.ProcessId
        foreach ($grandchild in $grandchildren) { Stop-Process -Id $grandchild.ProcessId -ErrorAction SilentlyContinue }
        Stop-Process -Id $child.ProcessId -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $ownedProcess.Id -ErrorAction SilentlyContinue
    Write-Host "Stopped $($entry.kind) process $($entry.id)."
}
