$Root = $PSScriptRoot
$PidFile = Join-Path $Root ".run-logs\pids.txt"

if (-not (Test-Path $PidFile)) {
    Write-Host "No OrganicKart processes are currently tracked."
    exit 0
}

$pids = @(
    Get-Content -Path $PidFile |
    Where-Object { $_ -match '^\d+$' }
)

$stopped = @()

foreach ($pidText in $pids) {

    $processId = [int]$pidText

    try {
        Get-Process -Id $processId -ErrorAction Stop | Out-Null

        Write-Host "Stopping process tree: $processId"

        & taskkill.exe /PID $processId /T /F 2>$null | Out-Null

        $stopped += $processId
    }
    catch {
        Write-Host "Process $processId is already stopped."
    }
}

Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue

Write-Host ""

if ($stopped.Count -gt 0) {
    $stoppedIds = ($stopped | Sort-Object -Unique) -join ", "
    Write-Host "Stopped OrganicKart process trees: $stoppedIds"
}
else {
    Write-Host "No OrganicKart processes were active."
}

Write-Host "OrganicKart stopped."