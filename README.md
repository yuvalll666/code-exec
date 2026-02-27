## Python Code Execution Engine

This service exposes a FastAPI HTTP API that executes untrusted Python code inside short‑lived Docker containers with strict resource limits.

The codebase is split into:
- **API service** (`services/api`): FastAPI app and HTTP routing.
- **Worker library** (`services/worker`): Docker interaction and sandboxed execution.
- **Shared config/logging** (`shared/core`): Centralised settings and logging configuration.

---

### Environment configuration

Runtime configuration is managed by `shared.core.config.Settings`, which reads from both environment variables and an optional `.env` file in the project root.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PROJECT_NAME` | Display name for the API. | `Python Code Execution Engine` |
| `API_V1_STR` | Base path for versioned API routes. | `/api/v1` |
| `DOCKER_IMAGE` | Base image used for sandbox containers. | `python:3.10-slim` |
| `MAX_CONCURRENT_CONTAINERS` | Max number of containers executing in parallel. | `3` |
| `CONTAINER_MEM_LIMIT` | Memory limit per container (Docker `mem_limit` syntax). | `128m` |
| `CONTAINER_TIMEOUT` | Max execution time in seconds before a container is killed. | `5` |
| `CONTAINER_PIDS_LIMIT` | Max number of processes allowed inside a container. | `50` |
| `CONTAINER_STORAGE_LIMIT_MB` | Max container writable layer size in MB. | `100` |
| `NETWORK_DISABLED` | Whether to disable networking inside execution containers. | `True` |
| `CONTAINER_USER` | UID:GID used inside execution containers. | `1000:1000` |

You can set these either via a `.env` file in the repo root or by exporting them in your shell.

Example `.env`:

```env
MAX_CONCURRENT_CONTAINERS=5
CONTAINER_TIMEOUT=10
CONTAINER_MEM_LIMIT=256m
DOCKER_IMAGE=python:3.10-slim
```

---

### Running locally (without Docker Compose)

**Prerequisites**
- Python 3.10+
- Docker Desktop / Docker Engine running (the API talks to the Docker daemon).

**1. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r services/api/requirements.txt
```

**3. Configure environment (optional)**

Either create a `.env` file as shown above, or set variables directly, for example on Windows PowerShell:

```powershell
$env:MAX_CONCURRENT_CONTAINERS=10
```

**4. Start the API**

Run from the project root so `services` and `shared` are importable:

```bash
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`, with the health check at `/health`.

> **Note:** Dependencies are intentionally split per service. The API installs from `services/api/requirements.txt`, and the worker from `services/worker/requirements.txt`. This keeps each image smaller and the responsibility of each service clear.

---

### Running with Docker Compose

The repository includes a `docker-compose.yml` that brings up:
- **api**: FastAPI application (builds from `services/api/Dockerfile`).
-, **worker**: A separate worker image (builds from `services/worker/Dockerfile`) prepared for a future queue-based architecture.
- **redis**: Redis instance for future use (e.g. as a queue or cache).
- **postgres**: Postgres instance for future use (e.g. storing execution metadata).

Both `api` and `worker` share the same environment configuration via `.env` and are attached to a shared Docker network.

**Prerequisites**
- Docker Desktop / Docker Engine with Docker Compose support.

**1. Create a `.env` file (optional but recommended)**

At the project root:

```env
MAX_CONCURRENT_CONTAINERS=5
CONTAINER_TIMEOUT=10
CONTAINER_MEM_LIMIT=256m
DOCKER_IMAGE=python:3.10-slim
```

**2. Start the stack**

From the project root:

```bash
docker compose up --build
```

This will:
- Build the `api` and `worker` images using their respective Dockerfiles.
- Start `api`, `worker`, `redis`, and `postgres` services on a shared network.
- Expose the API on `http://localhost:8000`.

> **Note:** The compose file mounts `/var/run/docker.sock` into both the `api` and `worker` containers so they can talk to the host Docker daemon. This works naturally on Linux and Docker Desktop with a Linux backend. On non-Linux setups you may need to adjust the mount or configure `DOCKER_HOST` according to your Docker installation.

---

### How things work (high level)

- **Concurrency control**: The worker library uses an `asyncio.Semaphore` (`MAX_CONCURRENT_CONTAINERS`) to throttle how many execution containers can run at once.
- **Sandboxing**: Each code execution runs in its own Docker container with no network, limited memory, tight PID and storage limits, and a non-root user.
- **Observability**: Each request is tagged with a short `request_id` which appears in logs end-to-end.
- **Cleanup**: Temporary files and containers are cleaned up automatically after each execution so the host stays tidy.  


### Update Database Schema

```bash
# 1. Create a new migration script based on model changes
alembic revision --autogenerate -m "describe_your_change"

# 2. Implement the changes in the database
alembic upgrade head