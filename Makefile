.PHONY: dev server test install lint format

dev:
	python start_server.py

server:
	uv run uvicorn app.main:server --host 0.0.0.0 --port 8000 --reload

run: server

test:
	python test_api.py

install:
	uv sync --dev

lint:
	ruff check app/

format:
	ruff format app/
