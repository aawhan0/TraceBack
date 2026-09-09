# TraceBack frontend

React + Vite frontend for the TraceBack investigation workspace.

## Development

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://127.0.0.1:5173` and proxies TraceBack API requests to `http://127.0.0.1:8000`.

Start the backend separately:

```bash
uvicorn app.main:app --reload
```

## Production build

```bash
npm run build
npm run preview
```

The frontend intentionally stays small: Investigate, Experiments, and History. It uses the existing FastAPI contracts rather than duplicating backend logic.
