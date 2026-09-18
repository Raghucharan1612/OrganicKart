# OrganicKart Frontend

## Frontend startup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The app runs on Vite at http://localhost:5173.

## API Gateway URL

The frontend communicates only through the API Gateway:

- Gateway: http://localhost:8000
- API base: http://localhost:8000/api/v1

This is configured in the frontend environment as `VITE_API_BASE_URL`.

## Authentication flow

1. User registers through `/api/v1/auth/register` via the gateway.
2. User logs in through `/api/v1/auth/login` via the gateway.
3. The backend returns a JWT access token.
4. The frontend stores the token in `localStorage` under `organickart_token`.
5. Every request uses the Axios interceptor in `src/services/apiClient.js` to send:
   `Authorization: Bearer <access_token>`
6. Unauthenticated or invalid tokens are cleared and the user is redirected to login.

## API client architecture

- `src/services/apiClient.js` is the single Axios instance.
- Resource-specific services such as `authService.js`, `productService.js`, `userService.js`, `orderService.js`, and `deliveryService.js` call that client.
- No frontend module should call downstream service ports directly.

## Environment variables

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Guest browsing

Unauthenticated users can browse the public catalog:

- homepage
- product listing
- product detail pages

Guest users do not have access to:

- cart
- checkout
- orders
- delivery
- profile

## Protected routes

Protected routes are enforced by the frontend route guards:

- `/profile`
- `/addresses`
- `/cart`
- `/checkout`
- `/orders`
- `/delivery`

Unauthenticated users are redirected to `/login`.

## Role-based UI behavior

Frontend role checks mirror the backend roles, including `CUSTOMER`, `ADMIN`, and `SUPER_ADMIN`.

These checks are for UI/UX only; backend authorization remains the source of truth.
