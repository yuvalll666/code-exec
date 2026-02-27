FROM python:3.11-slim

WORKDIR /app

# Copy the requirements from the api folder
COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project so the API can see the "shared" folder
COPY . .

# Run the API
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]