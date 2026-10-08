$Root = $PSScriptRoot
$LogsDir = Join-Path $Root ".run-logs"
$PidFile = Join-Path $LogsDir "pids.txt"

New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null

function Test-PortInUse {
    param(
        [int]$Port
    )

    try {
        $connection = Get-NetTCPConnection `
            -LocalPort $Port `
            -State Listen `
            -ErrorAction Stop

        return ($null -ne $connection)
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

    $command = "& '$Executable' $Arguments 2>&1 | Tee-Object -FilePath '$LogPath'"

    $process = Start-Process `
        -FilePath "powershell.exe" `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -PassThru `
        -ArgumentList @(
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $command
        )

    Write-Host "Started $Name (PID $($process.Id), Port $Port)"

    return $process.Id
}

$serviceDefinitions = @(

    @{
        Name = "User Service"
        Port = 8001
        WorkingDirectory = Join-Path $Root "services\user_service"
        Executable = Join-Path $Root "services\user_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8001"
        LogPath = Join-Path $LogsDir "user.log"
    },

    @{
        Name = "AI Service"
        Port = 8002
        WorkingDirectory = Join-Path $Root "services\ai_service"
        Executable = Join-Path $Root "services\product_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn app.main:app --host 127.0.0.1 --port 8002"
        LogPath = Join-Path $LogsDir "ai.log"
    },

    @{
        Name = "Product Service"
        Port = 8003
        WorkingDirectory = Join-Path $Root "services\product_service"
        Executable = Join-Path $Root "services\product_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8003"
        LogPath = Join-Path $LogsDir "product.log"
    },

    @{
        Name = "Order Service"
        Port = 8004
        WorkingDirectory = Join-Path $Root "services\order_service"
        Executable = Join-Path $Root "services\order_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8004"
        LogPath = Join-Path $LogsDir "order.log"
    },

    @{
        Name = "Delivery Service"
        Port = 8005
        WorkingDirectory = Join-Path $Root "services\delivery_service"
        Executable = Join-Path $Root "services\delivery_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8005"
        LogPath = Join-Path $LogsDir "delivery.log"
    },

    @{
        Name = "Notification Service"
        Port = 8006
        WorkingDirectory = Join-Path $Root "services\notification_service"
        Executable = Join-Path $Root "services\notification_service\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8006"
        LogPath = Join-Path $LogsDir "notification.log"
    },

    @{
        Name = "API Gateway"
        Port = 8000
        WorkingDirectory = Join-Path $Root "services\api_gateway"
        Executable = Join-Path $Root "services\api_gateway\.venv\Scripts\python.exe"
        Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8000"
        LogPath = Join-Path $LogsDir "gateway.log"
    },

    @{
        Name = "Frontend"
        Port = 5173
        WorkingDirectory = Join-Path $Root "frontend"
        Executable = "npm.cmd"
        Arguments = "run dev -- --host 127.0.0.1 --port 5173"
        LogPath = Join-Path $LogsDir "frontend.log"
    }
)
$startedPids = @()

foreach ($service in $serviceDefinitions) {

    if ($service.Name -eq "Frontend") {

        if (Test-PortInUse -Port $service.Port) {
            Write-Host "Port $($service.Port) is already in use - skipping Frontend"
            continue
        }

        $frontendCommand = "npm run dev -- --host 127.0.0.1 --port 5173 2>&1 | Tee-Object -FilePath '$($service.LogPath)'"

        $frontendProcess = Start-Process `
            -FilePath "powershell.exe" `
            -WorkingDirectory $service.WorkingDirectory `
            -WindowStyle Hidden `
            -PassThru `
            -ArgumentList @(
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                $frontendCommand
            )

        Write-Host "Started Frontend (PID $($frontendProcess.Id), Port 5173)"
        $startedPids += $frontendProcess.Id

        continue
    }

    $startedPid = Start-ManagedProcess `
        -Name $service.Name `
        -Port $service.Port `
        -WorkingDirectory $service.WorkingDirectory `
        -Executable $service.Executable `
        -Arguments $service.Arguments `
        -LogPath $service.LogPath

    if ($null -ne $startedPid) {
        $startedPids += $startedPid
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