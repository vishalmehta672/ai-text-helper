# API Design — Interview Notes

Quick reference notes on common backend API design questions.

---

## 1. Why POST?

**Short answer:** POST is used for sending data to the server.

**Better, production-focused answer:**

Consider a request that sends a large body:

```json
{
    "text": "Very long paragraph..."
}
```

Here we are *sending* data to the server, not just fetching it.

### POST is designed for:
- Sending a request body
- Creating or processing data
- Large payloads

### GET is designed for:
Fetching information using clean, resource-style URLs:

```
/products
/users
/orders
```

### Why not GET for this case?

If we tried to send large data through a GET request:

```
/api/v1/summarize?text=1000_words_here
```

We run into problems:
- The URL becomes huge
- It's not secure (data sits in the URL/logs)
- It's hard to manage

So the standard approach is:

```
POST /summarize
```

---

## 2. Why a Health Endpoint?

**Short answer:** It checks project health and the status of dependent services.

**Better, production-focused answer:**

In a real deployment, traffic flows through multiple layers:

```
Load Balancer
      ↓
FastAPI
      ↓
Database
```

Orchestration systems like **AWS** or **Kubernetes** periodically call:

```
GET /health
```

(for example, every 30 seconds).

### What happens if health fails?

```
Server unhealthy
      ↓
Remove from traffic
```

This prevents users from being routed to a broken server.

This is why almost every production service exposes a `/health` endpoint — it lets infrastructure automatically detect and route around unhealthy instances.

---

## 3. What is a Service Layer?

The **Service Layer** is an architectural pattern that sits between the controller (the route) and the data/business logic. It contains the **"brains"** of your application.

```
Route (Controller)
      ↓
Service Layer  ← business logic lives here
      ↓
Data / External APIs
```

### Why not keep logic inside routes?

1. **Separation of Concerns** — Routes should only handle HTTP concerns (parsing input, status codes, response headers). They shouldn't care *how* a summary is generated.
2. **Reusability** — If you later add a CLI tool or a background task processor, you can import the `TextSummarizer` class directly, without needing to simulate HTTP requests.
3. **Testability** — You can write unit tests for `TextSummarizer` independently of the web framework, making tests faster and more reliable.

---

## 4. Why is `print()` Not Suitable for Production?

**Short answer:** `print()` has no levels, no structure, and no control — it's fine for local debugging but breaks down in a real deployment.

**Better, production-focused answer:**

1. **No severity levels** — you can't distinguish an informational message from a warning or a critical error. `logger.info()` / `logger.error()` let you filter and prioritize; `print()` treats everything the same.
2. **No structure/context** — a real logger (like the one in `app/core/logger.py`) automatically attaches a timestamp, logger name, and level to every line, which is essential for debugging issues after the fact. `print()` gives you just the raw text.
3. **No control over output destination** — logs typically need to go to files, log aggregators, or monitoring systems (e.g., CloudWatch, Datadog), not just stdout. Loggers support handlers to route output anywhere; `print()` is stuck writing to stdout.
4. **No way to turn it off/down** — you can't selectively silence `print()` statements in production without deleting code. With logging, you set the level (e.g., `INFO` vs `DEBUG`) and control verbosity without touching source.
5. **Performance/buffering issues** — `print()` can block or behave unexpectedly under async/multi-process servers (like Uvicorn workers); logging libraries are built to handle concurrent/production environments safely.
6. **Leaks raw output to users** — an uncaught exception with `print()`-style tracebacks can expose internal stack traces to API clients, which is a security/information-disclosure risk. Proper logging keeps that internal, while the API returns a clean error (see the `try/except` + `HTTPException` pattern in `app/api/v1/routes.py`).

---

## 5. Unit Testing the Service Layer

**Short answer:** Test the smallest piece of pure logic (the service) directly, so failures point to the *logic*, not to routing, validation, or serialization.

**Better, production-focused answer:**

We wrote the first tests against `TextSummarizer.summarize()` in `app/services/service.py`, **not** the route. This is the **testing pyramid** idea — lots of cheap, fast unit tests at the bottom, fewer expensive integration/route tests above.

```
        /\        few   → route / integration tests (HTTP, TestClient)
       /  \
      /____\      many  → unit tests (pure service logic)
```

### Why service first, not the route?
1. **Fast** — no server spin-up, no `TestClient`, just a direct function call.
2. **Clear blame** — if a unit test fails, the *summarization logic* broke, not routing or validation.
3. **Fewer moving parts** — no fake HTTP request to build or mock.

### The AAA pattern (structure of every test)
```
Arrange → build the input / object
Act     → call the thing under test
Assert  → verify the result
```

### What we tested
| Case | Input | What it verifies |
|------|-------|------------------|
| returns text | any string | return type is `str` (contract check) |
| normal paragraph | 25 words | truncates to exactly the first 20 words |
| short text | 4 words | short input comes back unchanged (slicing past the end doesn't error) |

### Testing correct *failure*, not just success
Good code fails **predictably** on bad input. We use `with pytest.raises(...)` for this — it is itself an assertion ("this block **must** raise this error"), so no separate `assert` is needed inside it.

```python
with pytest.raises(ValueError):
    summarizer.summarize("")     # empty string -> nothing to summarize
```

### `TypeError` vs `ValueError` (Python convention)
- **`TypeError`** = wrong *type* (`None`, `123`, a list — not a `str` at all).
- **`ValueError`** = right type, wrong *value* (`""` or whitespace-only string).

This led us to add **input-validation guards** in the service (fail fast) so bad input raises a clean, intentional error instead of a confusing `AttributeError` deep inside `.split()`.

```python
if not isinstance(text, str):
    raise TypeError(...)   # wrong type
if not text.strip():
    raise ValueError(...)  # empty / whitespace value
```

### How to run
```bash
source venv/bin/activate
python -m pytest tests/test_summarizer.py -v
```
Use `python -m pytest` (not bare `pytest`) so the project root is on `sys.path` and `from app.services... import` resolves.

---

### Key Takeaways

| Concept         | Purpose                                                        |
|-----------------|----------------------------------------------------------------|
| `POST`          | Send body, create/process data, handle large payloads          |
| `GET`           | Fetch information via clean resource URLs                       |
| `/health`       | Let load balancers / K8s detect unhealthy servers and reroute  |
| Service Layer   | Hold business logic separately for clean, reusable, testable code |
| Logging         | Structured, leveled, redirectable output — unlike `print()`   |
| Unit Tests      | Verify pure service logic directly — fast, isolated, clear failures |
| CI (Actions)    | Run the suite on a clean machine on every push/PR, so "works on my laptop" bugs surface early |

---

# Daily Log

## 23 July 2026 — Testing & CI Day

### Today I learned

**Testing**
- Test the **service layer first**, not the route — it's pure logic, so failures point at the logic itself instead of routing/validation/serialization. Testing pyramid: many cheap unit tests at the bottom, fewer integration tests above.
- Every test follows **AAA**: Arrange → Act → Assert.
- `pytest.raises(...)` **is itself an assertion** — it tests that code fails *correctly*. No separate `assert` needed inside it, and any line after the raising call inside the block never runs.
- **`TypeError` vs `ValueError`**: wrong *type* vs right type but wrong *value*. Added fail-fast guards to `summarize()` for both.
- **Boundary testing** — the limit is 20, so 20 and 21 are the risky numbers. This is where off-by-one bugs hide; a 25-word test would never catch `[:19]`.
- **`@pytest.mark.parametrize`** — one test body, many inputs, and each input becomes its own reported test (better than a `for` loop, which stops at the first failure).
- **`exc_info`** — capture the exception to assert on its *message*, not just its type. The assert must sit outside the `with` block.
- Reading tracebacks: **`>` marks the failing line, `E` marks the error detail**. In diffs, `-` is expected and `+` is actual. `AssertionError` = code is wrong; `AttributeError`/`NameError` = the *test* is probably wrong.

**CI/CD**
- Workflows live in `.github/workflows/`. That path is fixed — it's a **GitHub** convention.
- **Git ≠ GitHub.** Git is the local tool that carries the file; GitHub is the platform that reads it and runs it. `git commit` alone does nothing — **push is the trigger**.
- Workflow anatomy: `on:` (when) → `jobs:` → `runs-on:` (which machine) → `steps:` (`uses:` for ready-made actions, `run:` for shell commands). `actions/checkout` must come first — the fresh VM starts empty.

**Real bugs found today**
- `requirements.txt` was a **`pip freeze` of the whole Anaconda `base` env** — 486 lines, 295 of them local `file:///` paths, plus an `-e /Users/.../Leo/hostfully-python` from a totally different project. Worse: **`fastapi` and `uvicorn` weren't even in it.** Lesson: never run `pip freeze` outside the project venv.
- Discovered a hidden behaviour: `split()` + `join()` **collapses all whitespace** (multiple spaces, tabs, newlines) and strips the ends. Nobody designed that — writing tests exposed it. Tests that lock in existing behaviour like this are called **characterization tests**.

### Biggest confusion

**Why CI wasn't running.** I pushed, the commit reached GitHub, but no workflow appeared — no icon next to the commit, zero results in the Actions tab. I assumed my YAML was broken and nearly started changing a file that was actually correct.

It turned out **GitHub Actions was in a partial outage** (Webhooks degraded — and webhooks are exactly what turns a push into a workflow run). Git Operations were fine, which is why `git push` worked and the whole site looked normal.

The confusing part was that **github.com looked completely healthy**. Outage status lives on a *different* site: **githubstatus.com**. "Partial outage" means some services are down while the rest work fine — it doesn't look like anything is broken from the outside.

Smaller confusions along the way:
- Why `pytest.raises` needs no `assert` after it (because it *is* the assert).
- Why `python -m pytest` works but bare `pytest` doesn't (`-m` puts the project root on `sys.path`).
- That `claude -c` is a **terminal** command, not something you type into the chat.

### One thing I found interesting

**18 passing tests, and the app still couldn't start.**

We deliberately introduced a typo in `app/main.py` (`FastAPI` → `FastAPIII`) and ran the suite:

```
18 passed  ✅        # tests
NameError: name 'FastAPIII' is not defined  ❌   # actually importing the app
```

Green CI, broken app. The reason: **every one of my tests imports only `app/services/service.py`.** `main.py`, `routes.py`, and `schemas/text.py` are never imported by any test, so no test can ever catch a bug in them.

That reframed testing for me. Coverage isn't about how many tests you have — it's about **which files they actually touch**. A 2-line **smoke test** (`from app.main import app`) would have caught this instantly.

### Questions for mentor

1. **Smoke tests** — is importing the app enough, or should the smoke test also hit `/health` through `TestClient`? Where's the line between a smoke test and an integration test?
2. **Linting order in CI** — should `ruff` / `mypy` be separate steps before `pytest`, or a separate job that runs in parallel? Fail-fast says put the fast checks first, but parallel gives you *all* the failures at once. Which is better in practice?
3. **How much should tests document behaviour?** The whitespace-collapsing was accidental. By writing tests for it, have I now *locked in* something I might want to change later? When is a characterization test protection, and when is it a cage?
4. **Route error handling** — `routes.py` currently catches every `Exception` and returns `500`. Now that the service raises `ValueError`/`TypeError` for bad input (a *client* mistake), those should be `400`. What's the clean pattern — catch specific exceptions in the route, or use a FastAPI exception handler?
5. **When is a test not worth writing?** I now have 18 tests for one 10-line function. Where's the point of diminishing returns?
6. **Pinning versions** — I pinned exact versions (`fastapi==0.136.3`). Is that right for an app, and does the answer change for a library? How do teams keep pins from going stale?