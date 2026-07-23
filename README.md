# AI Text Helper

[![Python Tests](https://github.com/vishalmehta672/ai-text-helper/actions/workflows/python-tests.yml/badge.svg)](https://github.com/vishalmehta672/ai-text-helper/actions/workflows/python-tests.yml)

AI-powered text processing service built with FastAPI.

## Features

- Health Check
- Summarization (Coming Soon)
- Categorization (Coming Soon)

## Completed Features

- ✅ FastAPI
- ✅ API Versioning
- ✅ Request Validation
- ✅ Service Layer
- ✅ Configuration
- ✅ Logging
- ✅ Unit Tests (pytest)
- ✅ CI Pipeline (GitHub Actions)

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Testing

Tests live in `tests/` and cover the service layer (`app/services/service.py`).

### Run Tests

```bash
pytest
```

Run from the project root with the virtual environment active. If imports such as
`from app.services.service import ...` fail, use `python -m pytest` instead — that
puts the project root on `sys.path`.

### Useful Options

```bash
pytest -v            # show each test name and its result
pytest -q            # compact output
pytest --lf          # re-run only the tests that failed last time
pytest -x            # stop at the first failure
pytest -k boundary   # run only tests whose name matches "boundary"
```

### What Is Covered

- Return type is always a string
- Long text is truncated to the first 20 words
- Short text is returned unchanged
- Boundary cases at exactly 20 and 21 words
- Whitespace (extra spaces, tabs, newlines) is collapsed
- Empty or whitespace-only input raises `ValueError`
- Non-string input (`None`, `int`, `float`, `list`, `dict`) raises `TypeError`
- Error messages name the offending type / problem

## CI Status

Every `push` and `pull_request` triggers the
[Python Tests](.github/workflows/python-tests.yml) workflow on GitHub Actions.

The workflow runs on a clean `ubuntu-latest` machine and will:

1. Check out the repository
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Run the test suite with `pytest`

The badge at the top of this file reflects the latest run on `main`. Live status:
[Actions tab](https://github.com/vishalmehta672/ai-text-helper/actions).
