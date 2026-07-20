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

### Key Takeaways

| Concept         | Purpose                                                        |
|-----------------|----------------------------------------------------------------|
| `POST`          | Send body, create/process data, handle large payloads          |
| `GET`           | Fetch information via clean resource URLs                       |
| `/health`       | Let load balancers / K8s detect unhealthy servers and reroute  |
| Service Layer   | Hold business logic separately for clean, reusable, testable code |
| Logging         | Structured, leveled, redirectable output — unlike `print()`   |