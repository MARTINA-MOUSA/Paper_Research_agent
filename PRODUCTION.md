# Production Deployment Guide

## Overview
This guide covers deploying Paper2Video API to production environments.

## Prerequisites
- Docker and Docker Compose (recommended)
- OR Python 3.11+ with virtual environment
- Gemini API Key
- Server with sufficient resources (4GB+ RAM recommended for video processing)

## Quick Start with Docker

1. **Clone and configure:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

2. **Build and run:**
```bash
docker-compose up -d --build
```

3. **Check health:**
```bash
curl http://localhost:8000/health
```

## Production Deployment Options

### Option 1: Docker (Recommended)

**Docker Compose:**
```bash
docker-compose up -d
```

**Manual Docker:**
```bash
docker build -t paper2video .
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  paper2video
```

### Option 2: Gunicorn (Direct)

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env
```

3. **Run with Gunicorn:**
```bash
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

Or use the provided script:
```bash
chmod +x start.sh
./start.sh
```

### Option 3: Systemd Service

Create `/etc/systemd/system/paper2video.service`:
```ini
[Unit]
Description=Paper2Video API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/paper2video/backend
Environment="PATH=/opt/paper2video/backend/venv/bin"
ExecStart=/opt/paper2video/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable paper2video
sudo systemctl start paper2video
```

## Reverse Proxy (Nginx)

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
    }
}
```

## Environment Variables

Required:
- `GEMINI_API_KEY`: Your Google Gemini API key

Optional:
- `DATABASE_URL`: Database connection string (default: SQLite)
- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 4)
- `CORS_ORIGINS`: Comma-separated allowed origins (default: *)
- `MAX_FILE_SIZE`: Max upload size in bytes (default: 10MB)
- `LOG_LEVEL`: Logging level (default: INFO)

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_configured": true
}
```

### Logs
- Application logs: `backend/logs/app.log`
- Docker logs: `docker-compose logs -f`
- Systemd logs: `journalctl -u paper2video -f`

## Performance Tuning

1. **Worker Count:**
   - Formula: `(2 × CPU cores) + 1`
   - Adjust `WORKERS` in `.env` or docker-compose

2. **Database:**
   - For high traffic, use PostgreSQL instead of SQLite
   - Update `DATABASE_URL` in `.env`

3. **File Storage:**
   - Use external storage (S3, etc.) for `outputs/` directory
   - Implement cleanup job for old videos

4. **Caching:**
   - Consider Redis for caching Gemini API responses
   - Cache trending papers results

## Security Checklist

- [ ] Set specific `CORS_ORIGINS` (not `*`)
- [ ] Use HTTPS with SSL certificate
- [ ] Keep dependencies updated
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets (never commit `.env`)
- [ ] Implement rate limiting (consider adding)
- [ ] Regular backups of database

## Scaling

### Horizontal Scaling
- Use a load balancer (Nginx, HAProxy)
- Multiple instances behind load balancer
- Shared database (PostgreSQL)
- Shared file storage (S3, NFS)

### Vertical Scaling
- Increase `WORKERS` based on CPU cores
- Increase server RAM for video processing
- Use SSD storage for better I/O

## Troubleshooting

**Issue: Video generation fails**
- Check ffmpeg installation: `ffmpeg -version`
- Ensure sufficient disk space
- Check logs for TTS errors

**Issue: Slow responses**
- Reduce `MAX_TEXT_LENGTH` in config
- Increase worker count
- Use faster storage (SSD)

**Issue: Database locks (SQLite)**
- Switch to PostgreSQL for production
- Reduce concurrent writes

## Backup

**Database:**
```bash
# SQLite
cp app.db backups/app_$(date +%Y%m%d).db
```

**Files:**
```bash
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/
tar -czf backups/outputs_$(date +%Y%m%d).tar.gz outputs/
```

## Updates

1. Pull latest code
2. Rebuild Docker image: `docker-compose build`
3. Restart: `docker-compose restart`
4. Or with zero downtime: `docker-compose up -d --no-deps`

## Support

Check logs first:
- `backend/logs/app.log`
- `docker-compose logs api`

Common issues:
- Missing API key → Check `.env`
- Port already in use → Change `PORT` in `.env`
- Disk full → Clean up old videos in `outputs/`

