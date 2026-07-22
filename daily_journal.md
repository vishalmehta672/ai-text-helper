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