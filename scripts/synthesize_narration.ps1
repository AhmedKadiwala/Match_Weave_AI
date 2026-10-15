$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$repo = Split-Path -Parent $PSScriptRoot
$audioDir = Join-Path $repo 'runtime\narration'
New-Item -ItemType Directory -Force -Path $audioDir | Out-Null
$segments = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $repo 'demos\narration-segments.json')))
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100
$index = 0
foreach ($segment in $segments) {
    $destination = Join-Path $audioDir ('segment-{0:D2}.wav' -f $index)
    $synth.SetOutputToWaveFile($destination)
    $synth.Speak([string]$segment.text)
    $synth.SetOutputToNull()
    Write-Host "Rendered narration segment $index"
    $index++
}
$synth.Dispose()
