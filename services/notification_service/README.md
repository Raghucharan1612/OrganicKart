# Notification Service

Standalone FastAPI service for user-owned in-app notifications.

## Runtime

- Port: `8006`
- Database: `organickart_notification_db`
- Runtime URL: `NOTIFICATION_DATABASE_URL` in `.env`
- Driver: SQLAlchemy with PyMySQL

Start locally:

```powershell
cd services/notification_service
python -m uvicorn main:app --host 0.0.0.0 --port 8006
```

## API

All public notification reads require the shared Bearer JWT. The `sub` claim determines ownership.

- `GET /api/v1/notifications`
- `GET /api/v1/notifications/{notification_id}`
- `PATCH /api/v1/notifications/{notification_id}/read`
- `PATCH /api/v1/notifications/read-all`
- `POST /api/v1/notifications`

Creation is restricted to `ADMIN`/`SUPER_ADMIN` JWTs or the environment-based `X-Internal-Service-Key` used by trusted service trigger calls. Customer reads never query another service database.

## Lifecycle and idempotency

In-app notifications start as `PENDING` and become `READ` when acknowledged. Email notifications use `MockEmailSender` and become `SENT` without sending real email. A unique `(user_id, type, reference_type, reference_id)` event key prevents duplicate business notifications.

Current trigger integrations are intentionally small: user registration creates `WELCOME`, order creation creates `ORDER_CREATED`, and delivery status changes create the matching delivery notification. Real email providers and asynchronous event transport are future work.

## Testing

```powershell
python -m pytest -q
```

Tests use isolated SQLite fixtures. Runtime configuration remains MySQL.
