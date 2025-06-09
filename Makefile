.PHONY: run

run:
	uv run uvicorn app.main:app --host localhost --port 8000 --reload
