# OrganicKart

OrganicKart is a microservices-based marketplace with a React/Vite frontend and multiple FastAPI services behind an API gateway.

## Architecture

- Frontend: React + Vite
- API gateway: FastAPI service on port 8000
- User service: port 8001
- Product service: port 8003
- Order service: port 8004
- Delivery service: port 8005
- Notification service: port 8006
- MySQL databases remain service-owned and are not merged into a monolith.

## Project Structure

```
OrganicKart/
├── frontend/            # React SPA
├── services/
│   ├── api_gateway/     # Gateway proxy to downstream services
│   ├── user_service/
│   ├── product_service/
│   ├── order_service/
│   ├── delivery_service/
│   ├── notification_service/
│   └── ...
├── database/            # DB-level scripts/docs outside the service code
├── docs/                # Project docs and sprint notes
├── run_all.ps1          # Starts the full local stack
├── stop_all.ps1         # Stops the full local stack
├── README.md
└── AGENTS.md
```

## Startup

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Microservices
```bash
cd services/api_gateway
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Repeat for each service in `services/*` using the correct port and venv.

Access Swagger at:
- Gateway: http://localhost:8000/docs
- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8003/docs
- Order Service: http://localhost:8004/docs
- Delivery Service: http://localhost:8005/docs
- Notification Service: http://localhost:8006/docs

## Frontend API

The frontend must communicate only through the API Gateway:

- `VITE_API_BASE_URL=http://localhost:8000/api/v1`

The gateway forwards requests to the correct microservice while preserving the `Authorization` header and request payload.

