import os
import subprocess
import time
from pathlib import Path

import httpx
import sqlalchemy as sa
from dotenv import dotenv_values

root = Path(__file__).resolve().parent
os.chdir(root)
env = dotenv_values(root / '.env')
python_exe = root / '.venv' / 'Scripts' / 'python.exe'
service_url = 'http://localhost:8006'


def kill_port_8006():
    subprocess.run(
        ['powershell', '-NoProfile', '-Command', "Get-NetTCPConnection -LocalPort 8006 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
        check=False,
    )
    time.sleep(2)


def wait_for_health(timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = httpx.get(f'{service_url}/health', timeout=5)
            print('HEALTH', r.status_code, r.text)
            return True
        except Exception as exc:  # pragma: no cover
            print('HEALTH_RETRY', type(exc).__name__, exc)
            time.sleep(1)
    raise RuntimeError('Service did not become healthy after restart')


def start_service(log_path):
    return subprocess.Popen(
        [str(python_exe), '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8006'],
        cwd=str(root),
        stdout=open(log_path, 'wb'),
        stderr=subprocess.STDOUT,
    )


kill_port_8006()
log_path = root / 'restart_validation.log'
proc = start_service(log_path)
try:
    wait_for_health()

    headers = {
        'X-Internal-Service-Key': env['INTERNAL_SERVICE_KEY'],
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
    resp = httpx.post(f'{service_url}/api/v1/notifications', json=payload, headers=headers, timeout=20)
    print('POST_STATUS', resp.status_code)
    print('POST_BODY', resp.text)
    if resp.status_code != 201:
        raise RuntimeError(f'Create failed: {resp.text}')
    created_id = resp.json()['id']

    engine = sa.create_engine(env['NOTIFICATION_DATABASE_URL'], pool_pre_ping=True)
    with engine.connect() as conn:
        row = conn.execute(
            sa.text('SELECT id, user_id, type, status, title FROM notifications WHERE id = :id'),
            {'id': created_id},
        ).fetchone()
        print('DB_ROW_AFTER_POST', row)
        if row is None:
            raise RuntimeError('Notification row missing immediately after creation')

    proc.terminate()
    proc.wait(timeout=20)
    print('SERVICE_STOPPED')

    proc2 = start_service(log_path)
    try:
        wait_for_health()
        with engine.connect() as conn:
            rows_after_restart = conn.execute(
                sa.text('SELECT id, user_id, type, status, title FROM notifications WHERE user_id = :uid ORDER BY id DESC LIMIT 10'),
                {'uid': 1},
            ).fetchall()
            print('DB_ROWS_AFTER_RESTART', rows_after_restart)
        if not any(row[0] == created_id for row in rows_after_restart):
            raise RuntimeError(f'Expected notification id {created_id} missing after restart')
        print('RESTART_PERSISTENCE_OK')
    finally:
        proc2.terminate()
        proc2.wait(timeout=20)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=20)
    except Exception:
        pass
    print('VALIDATION_COMPLETE')
