# Task API

## Setup
```bash
# Run setup script (creates venv and installs dependencies)
./setup.sh
```

Or manually:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run
```bash
# Make sure venv is activated
source venv/bin/activate

# Run the API
uvicorn app.main:app --reload
```

## API Endpoints
- POST /tasks
- GET /tasks
- GET /tasks/{id}
- PUT /tasks/{id}
- DELETE /tasks/{id}
