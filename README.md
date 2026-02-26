# Python Code Execution Engine

.\venv\Scripts\activate.bat
uvicorn main:app --reload

## Configuration
The application uses environment variables for resource management.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `MAX_CONCURRENT_CONTAINERS` | Limits the number of simultaneous Docker containers to protect host CPU/RAM. | 3 |

## How to Run
To start the server with a custom concurrency limit (e.g., 10):

### Windows (PowerShell)
$env:MAX_CONCURRENT_CONTAINERS=10; python main.py

MAX_CONCURRENT_CONTAINERS=10 python main.py

## Key Features
- **Concurrency Control:** Uses an `asyncio.Semaphore` to throttle container execution.
- **Sandboxing:** Containers run with no network, limited memory (128MB), and as a non-root user.
- **Observability:** Each request is assigned a unique `request_id` for log tracing.
- **Cleanup:** Uses Python context managers (`with` statements) to ensure temporary files and containers are removed after execution.