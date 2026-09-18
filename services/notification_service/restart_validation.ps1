$ErrorActionPreference = 'Stop'
$root = 'C:\Users\RaghuCharan\Documents\vscode\DCL\OrganicKart'
$svc = Join-Path $root 'services\notification_service'
$py = Join-Path $svc '.venv\Scripts\python.exe'
$log = Join-Path $svc 'restart_validation.log'

function StopNotificationService {
    $existing = Get-NetTCPConnection -LocalPort 8006 -ErrorAction SilentlyContinue
    if ($existing) {
        foreach ($pid in ($existing | Select-Object -ExpandProperty OwningProcess -Unique)) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

StopNotificationService
Start-Process -FilePath $py -ArgumentList @('-m','uvicorn','main:app','--host','0.0.0.0','--port','8006') -WorkingDirectory $svc -RedirectStandardOutput $log -RedirectStandardError $log | Out-Null
Start-Sleep -Seconds 6
$health = Invoke-RestMethod -Uri 'http://localhost:8006/health' -Method Get
Write-Host "HEALTH:$($health | ConvertTo-Json -Compress)"

$pythonScript = @'
import os
import time
import httpx
import sqlalchemy as sa
from dotenv import dotenv_values
from jose import jwt

os.chdir(r'C:\Users\RaghuCharan\Documents\vscode\DCL\OrganicKart\services\notification_service')
env = dotenv_values('.env')
headers = {
    'Authorization': 'Bearer ' + jwt.encode({'sub': '1', 'role': 'ADMIN'}, env['JWT_SECRET_KEY'], algorithm=env['JWT_ALGORITHM']),
    'Content-Type': 'application/json',
}
payload = {
    'user_id': 1,
    'type': 'ORDER_CREATED',
    'title': 'Restart validation',
    'message': 'Row must persist after service restart',
    'channel': 'IN_APP',
    'reference_type': 'ORDER',
    'reference_id': 99991,
}
resp = httpx.post('http://localhost:8006/api/v1/notifications', json=payload, headers=headers, timeout=20)
print('POST_STATUS', resp.status_code)
print('POST_BODY', resp.text)
if resp.status_code != 201:
    raise RuntimeError(f'Create failed: {resp.text}')
created_id = resp.json()['id']
eng = sa.create_engine(env['NOTIFICATION_DATABASE_URL'], pool_pre_ping=True)
with eng.connect() as conn:
    row = conn.execute(sa.text('SELECT id, user_id, type, status, title FROM notifications WHERE id = :id'), {'id': created_id}).fetchone()
    print('DB_ROW_AFTER_POST', row)
    if row is None:
        raise RuntimeError('Notification row missing immediately after create')
'@
$pythonScript | & $py -

$proc = Get-NetTCPConnection -LocalPort 8006 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($proc) {
    foreach ($pid in $proc) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 2
Start-Process -FilePath $py -ArgumentList @('-m','uvicorn','main:app','--host','0.0.0.0','--port','8006') -WorkingDirectory $svc -RedirectStandardOutput $log -RedirectStandardError $log | Out-Null
Start-Sleep -Seconds 6
$health2 = Invoke-RestMethod -Uri 'http://localhost:8006/health' -Method Get
Write-Host "RESTART_HEALTH:$($health2 | ConvertTo-Json -Compress)"

$pythonCheck = @'
import os
import sqlalchemy as sa
from dotenv import dotenv_values

os.chdir(r'C:\Users\RaghuCharan\Documents\vscode\DCL\OrganicKart\services\notification_service')
env = dotenv_values('.env')
eng = sa.create_engine(env['NOTIFICATION_DATABASE_URL'], pool_pre_ping=True)
with eng.connect() as conn:
    rows = conn.execute(sa.text('SELECT id, user_id, type, status, title FROM notifications WHERE user_id = :uid ORDER BY id DESC LIMIT 10'), {'uid': 1}).fetchall()
    print('DB_ROWS_AFTER_RESTART', rows)
    if not rows:
        raise RuntimeError('No notifications found for user 1 after restart')
'@
$pythonCheck | & $py -
Write-Host 'RESTART_VALIDATION_OK'

# cleanup current service instance
$finalProc = Get-NetTCPConnection -LocalPort 8006 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($finalProc) {
    foreach ($pid in $finalProc) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
}
