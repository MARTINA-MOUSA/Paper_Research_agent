#!/bin/bash
# Production startup script

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations/initialize DB
python -c "from database.db import engine; from database import models; models.Base.metadata.create_all(bind=engine)"

# Start with Gunicorn
exec gunicorn main:app \
    -w ${WORKERS:-4} \
    -k uvicorn.workers.UvicornWorker \
    -b ${HOST:-0.0.0.0}:${PORT:-8000} \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}

