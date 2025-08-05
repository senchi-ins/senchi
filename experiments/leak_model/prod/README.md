# Leak Model API

A FastAPI server for leak prediction using the trained TCN model.

## Setup

### Prerequisites
- Python 3.11+
- uv (Python package manager)

### Installation
```bash
uv sync
```

## Running the API

### Local Development
```bash
uv run src/main.py
```

### Using Docker
```bash
docker-compose up --build
```

### Using the mock script
```bash
./mock.sh run server
```

## Testing
```bash
./mock.sh run tests
```

## API Endpoints

- `GET /health` - Health check
- `POST /predict?house_id=1` - Make predictions for a house

## Directory Structure
```
prod/
├── src/
│   ├── config.py
│   ├── main.py
│   ├── pipeline.py
│   ├── pred.py
│   └── utils.py
├── models/
│   ├── feature_scaler.pkl
│   └── tcn_fold5_20250805_084646.pt
├── test_data/
│   └── testing.py
├── output/
├── Dockerfile
├── docker-compose.yml
├── mock.sh
└── pyproject.toml
``` 