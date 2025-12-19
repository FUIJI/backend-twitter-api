# Backend Service

## ✨ Features

- Find tweets by hashtag
- Fetch tweets from specific users

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd backend-twitter-api

# Set environment variables
cp .env.example .env
# Edit .env and add your TWITTER_BEARER_TOKEN

# Docker
docker compose up -d --build

# Swagger UI
http://localhost:8000/docs
```

## 🧪 Testing

### Make Environment
```bash
# Create venv
python -m venv .venv
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v
```

## 📚 References
- [X API v2 Documentation](https://docs.x.com/x-api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)