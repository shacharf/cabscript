.PHONY: frontend binary clean dev

# Build the React frontend into src/cabinetry/app/static/
frontend:
	cd frontend && npm ci && npm run build

# Build the single-file binary (requires frontend to be built first)
binary: frontend
	uv run pyinstaller cabinet.spec

# Run the dev server (frontend proxies to this via Vite)
dev:
	uv run uvicorn cabinetry.app.main:app --reload --port 8000

# Remove build artifacts
clean:
	rm -rf dist/ build/ __pycache__
