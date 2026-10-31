$Root = $PSScriptRoot
$LogsDir = Join-Path $Root ".run-logs"
$PidFile = Join-Path $LogsDir "pids.txt"

New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null

function Test-PortInUse {
    param([int]$Port)
    try {
        $null = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Start-ManagedProcess {
    param(
        [string]$Name,
        [int]$Port,
        [string]$WorkingDirectory,
        [string]$Executable,
        [string]$Arguments,
        [string]$LogPath
    )

    if (Test-PortInUse -Port $Port) {
        Write-Host "Port $Port is already in use - skipping $Name"
        return $null
    }

    if (-not (Test-Path $WorkingDirectory)) {
        Write-Host "ERROR: Working directory not found: $WorkingDirectory"
        return $null
    }

    if (-not (Test-Path $Executable)) {
        Write-Host "ERROR: Executable not found: $Executable"
        return $null
    }

    # Use WMI/CIM Win32_Process to launch fully detached from the current job
    # object so the child survives after this script exits.
    $cmdLine = "`"$Executable`" $Arguments"
    $createFlags = 0x00000008  # DETACHED_PROCESS
    $startup = New-CimInstance -CimClass (Get-CimClass Win32_ProcessStartup) -Property @{
        ShowWindow = 0   # SW_HIDE
    } -ClientOnly

    $result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine       = $cmdLine
        CurrentDirectory  = $WorkingDirectory
        ProcessStartupInformation = $startup
    }

    if ($result.ReturnValue -ne 0) {
        Write-Host "ERROR: Failed to start $Name (Win32 error $($result.ReturnValue))"
        return $null
    }

    $processId = $result.ProcessId
    Write-Host "Started $Name (PID $processId, Port $Port)"

    return $processId
}

$serviceDefinitions = @(

    @{
        Name             = "User Service"
        Port             = 8001
        WorkingDirectory = Join-Path $Root "services\user_service"
        Executable       = Join-Path $Root "services\user_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8001"
        LogPath          = Join-Path $LogsDir "user.log"
    },

    @{
        Name             = "AI Service"
        Port             = 8002
        WorkingDirectory = Join-Path $Root "services\ai_service"
        Executable       = Join-Path $Root "services\ai_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn app.main:app --host 127.0.0.1 --port 8002"
        LogPath          = Join-Path $LogsDir "ai.log"
    },

    @{
        Name             = "Product Service"
        Port             = 8003
        WorkingDirectory = Join-Path $Root "services\product_service"
        Executable       = Join-Path $Root "services\product_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8003"
        LogPath          = Join-Path $LogsDir "product.log"
    },

    @{
        Name             = "Order Service"
        Port             = 8004
        WorkingDirectory = Join-Path $Root "services\order_service"
        Executable       = Join-Path $Root "services\order_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8004"
        LogPath          = Join-Path $LogsDir "order.log"
    },

    @{
        Name             = "Delivery Service"
        Port             = 8005
        WorkingDirectory = Join-Path $Root "services\delivery_service"
        Executable       = Join-Path $Root "services\delivery_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8005"
        LogPath          = Join-Path $LogsDir "delivery.log"
    },

    @{
        Name             = "Notification Service"
        Port             = 8006
        WorkingDirectory = Join-Path $Root "services\notification_service"
        Executable       = Join-Path $Root "services\notification_service\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8006"
        LogPath          = Join-Path $LogsDir "notification.log"
    },

    @{
        Name             = "API Gateway"
        Port             = 8000
        WorkingDirectory = Join-Path $Root "services\api_gateway"
        Executable       = Join-Path $Root "services\api_gateway\.venv\Scripts\python.exe"
        Arguments        = "-m uvicorn main:app --host 127.0.0.1 --port 8000"
        LogPath          = Join-Path $LogsDir "gateway.log"
    }
)

$startedPids = @()

foreach ($service in $serviceDefinitions) {

    $startedPid = Start-ManagedProcess `
        -Name             $service.Name `
        -Port             $service.Port `
        -WorkingDirectory $service.WorkingDirectory `
        -Executable       $service.Executable `
        -Arguments        $service.Arguments `
        -LogPath          $service.LogPath

    if ($null -ne $startedPid) {
        $startedPids += $startedPid
    }
}

# ── Frontend (npm run dev) ──────────────────────────────────────────────────
$frontendPort = 5173
$frontendLog  = Join-Path $LogsDir "frontend.log"
$frontendDir  = Join-Path $Root "frontend"

if (Test-PortInUse -Port $frontendPort) {
    Write-Host "Port $frontendPort is already in use - skipping Frontend"
}
else {
    # npm.cmd is a batch file; we launch cmd.exe so it resolves correctly
    $npmCmdObj = Get-Command npm.cmd -EA SilentlyContinue
    $npmCmd    = if ($npmCmdObj) { $npmCmdObj.Source } else { "npm.cmd" }
    $cmdLine  = "cmd.exe /c npm run dev -- --host 127.0.0.1 --port $frontendPort"
    $startup  = New-CimInstance -CimClass (Get-CimClass Win32_ProcessStartup) -Property @{ ShowWindow = 0 } -ClientOnly

    $result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine                = $cmdLine
        CurrentDirectory           = $frontendDir
        ProcessStartupInformation  = $startup
    }

    if ($result.ReturnValue -eq 0) {
        Write-Host "Started Frontend (PID $($result.ProcessId), Port $frontendPort)"
        $startedPids += $result.ProcessId
    }
    else {
        Write-Host "ERROR: Failed to start Frontend (Win32 error $($result.ReturnValue))"
    }
}

$startedPids |
    Sort-Object -Unique |
    Set-Content -Path $PidFile

Write-Host ""
Write-Host "========================================"
Write-Host "OrganicKart started"
Write-Host "========================================"
Write-Host "User Service       http://127.0.0.1:8001"
Write-Host "AI Service         http://127.0.0.1:8002"
Write-Host "Product Service    http://127.0.0.1:8003"
Write-Host "Order Service      http://127.0.0.1:8004"
Write-Host "Delivery Service   http://127.0.0.1:8005"
Write-Host "Notification       http://127.0.0.1:8006"
Write-Host "API Gateway        http://127.0.0.1:8000"
Write-Host "Frontend           http://127.0.0.1:5173"
Write-Host "========================================"