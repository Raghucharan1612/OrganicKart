# AGENTS.md

This repository is a microservices-based OrganicKart project with a React + Vite frontend and multiple FastAPI services behind an API gateway. Keep changes narrowly scoped to the relevant service or feature unless the task clearly spans multiple services.

## Project map

- Frontend: `frontend/`
  - Vite app, React, Redux Toolkit, React Router, Tailwind
  - App entry points and shared UI live under `frontend/src/`
  - API calls are centralized under `frontend/src/services/`
- Services: `services/`
  - `api_gateway/` proxies requests to downstream services
  - `user_service/`, `product_service/`, `order_service/`, `delivery_service/`, `notification_service/` each own their runtime domain and database
- Supporting folders:
  - `docs/` for sprint and architecture notes
  - `database/` for database-level docs/scripts
  - `docker/` reserved for containerization work if needed later

## Working conventions

- Prefer the existing architecture and naming patterns already in the codebase; do not introduce new app-wide patterns without a clear reason.
- Keep frontend and service changes separate unless the task specifically requires end-to-end integration.
- Favor targeted edits over broad refactors.
- When changing API contracts, keep the frontend and service schema layers in sync.
- Do not duplicate documentation already present in the repo; link to the relevant docs instead.
- The frontend must use the API Gateway and must not call downstream service ports directly.

## Key documentation

- Repo overview and setup: [README.md](README.md)
- Sprint and project docs: [docs/README.md](docs/README.md)
- Frontend package scripts: [frontend/package.json](frontend/package.json)

## Commands

### Frontend

```bash
cd frontend
npm install
npm run build
npm run lint
npm run dev
```

### Services

```bash
cd services/user_service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Use the matching service port and folder for each microservice.

## Product status

The repo is in an incremental implementation state. Sprint 1 and 2 features are complete, while catalog, checkout, orders, dashboards, and other later modules are still pending. Keep that in mind when adding or modifying behavior so new work aligns with the intended roadmap rather than assuming a full marketplace is already implemented.

## Good default behavior for AI agents

- Start by locating the exact feature area before editing.
- Confirm existing patterns in the relevant frontend or service module before guessing.
- Make the smallest necessary change and validate it with the closest relevant command.
- If a task touches auth, routing, RBAC, or user data flows, look at the existing service auth and frontend route guard patterns first.
