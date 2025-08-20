# PII Guardian Frontend

This app is built with React + Vite + Tailwind.

- Dev: `npm install` then `npm run dev` (Vite dev proxy forwards `/api` to `http://localhost:8000`).
- Build: `npm run build` then `npm run preview`.

Environment variables:

- `VITE_API_BASE` (optional): Set to your FastAPI base URL in production (e.g. `https://api.example.com`). Leave empty in development to use the proxy.
