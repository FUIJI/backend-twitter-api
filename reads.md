# Backend Service

A backend service built with **FastAPI** that retrieves public tweet data from **X (Twitter) API v2**.  
The project is intentionally kept simple, focusing on correctness, clarity, and maintainability without over-engineering.

---

## Features

- Retrieve recent tweets by hashtag
- Retrieve recent tweets from a specific user
- Clean and normalized JSON response format
- Direct HTTP integration with X API (no official or third-party SDKs)

---

## System Overview

```text
Client
  ↓
FastAPI REST API
  ↓
TwitterAPIClient (httpx)
  ↓
X (Twitter) API v2
```

The API layer handles request validation and HTTP responses

The service layer communicates directly with X API using HTTP requests

External API responses are transformed into a simplified format

Tweets are fetched in real time and are not stored persistently


## Quick Start

```text
Prerequisites
Python 3.11+
Docker & Docker Compose
```

## Run with Docker

```bash
# Clone repository
git clone <repository-url>
cd backend-twitter-api

# Set environment variables
cp .env.example .env
# Add your TWITTER_BEARER_TOKEN to the .env file

# Build and run
docker compose up -d --build

# API Documentation (Swagger UI):
http://localhost:8000/docs
```

## API Endpoints

### hashtag

```bash
GET /hashtags/{hashtag}

limit (optional, default: 30, max: 100)
```

### users

```bash
GET /users/{username}

limit (optional, default: 10, max: 100)
```

## Testing
Testing focuses on API behavior and core business logic.
External X (Twitter) API calls are mocked to ensure tests are fast, deterministic, and not affected by rate limits.

```bash
# Create virtual environment
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Environment Variables

```text
TWITTER_BEARER_TOKEN : X API Bearer Token (OAuth 2.0 App-only authentication)
For security reasons, the bearer token is not included in this repository.
```

## References

X API v2 Documentation: https://docs.x.com/x-api

FastAPI Documentation: https://fastapi.tiangolo.com/

## Note:  
The Twitter API client is not directly unit-tested to avoid brittle tests that mock external HTTP behavior.  
Service-layer tests cover all business logic and interactions with the client.