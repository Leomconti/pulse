.PHONY: dev server test install lint format


server:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run: server

test:
	python test_api.py

lint:
	ruff check app/ --fix

format:
	ruff format app/
