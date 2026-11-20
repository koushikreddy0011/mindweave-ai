# MindWeave AI — Production Operations & Deployment Runbook

This operations runbook details the architecture, configuration, deployment, backup/restore, SSL/TLS termination, and disaster recovery procedures for the **MindWeave AI** production platform.

---

## 1. Production Architecture Overview

MindWeave AI is deployed as a coordinated, multi-container architecture orchestrated via Docker Compose (`docker-compose.prod.yml`).

```
                              [ Internet / Clients ]
                                        │
                                        ▼ (Port 80 / 443)
                         ┌─────────────────────────────┐
                         │      Nginx Reverse Proxy     │
                         │   (Frontend Container: :80) │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
                 ▼ (/index.html, static assets)                ▼ (/api/v1/* reverse proxy)
      ┌─────────────────────┐                       ┌─────────────────────┐
      │  React 18 SPA (Nginx)│                       │  FastAPI (Uvicorn)  │
      │  Port 80 (Internal)  │                       │  Port 8000 (Internal)│
      └─────────────────────┘                       └──────────┬──────────┘
                                                               │ (asyncpg pool)
                                                               ▼
                                                    ┌─────────────────────┐
                                                    │ PostgreSQL 16 +     │
                                                    │ pgvector (Vector 768)│
                                                    │ Port 5432 (Internal)│
                                                    └─────────────────────┘
```

### Containers & Port Allocations

| Service | Container Name | Image / Base | Internal Port | Host Port | Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **db** | `mindweave_postgres_prod` | `pgvector/pgvector:pg16` | 5432 | 5432 | PostgreSQL relational storage + 768-dim vector embeddings |
| **backend** | `mindweave_backend_prod` | `python:3.11-slim` | 8000 | 8000 (proxied) | FastAPI, Alembic migrations, Gemini AI pipeline, PyMuPDF |
| **frontend** | `mindweave_frontend_prod`| `nginx:alpine` | 80 | 80 / 443 | Vite static build, Nginx proxy to backend `/api/v1` |

### Persistent Storage & Network

- **Docker Volume**: `postgres_prod_data` mounts to `/var/lib/postgresql/data` for transactional durability.
- **Docker Network**: `mindweave_prod_network` (isolated bridge network) connects all services.

---

## 2. Pre-requisites & Environment Secrets Configuration

### System Prerequisites
- Linux OS (Ubuntu 22.04 LTS / Debian 12 recommended)
- Docker Engine version 24.0+ and Docker Compose v2.20+
- Minimum Server Specs: 2 vCPU, 4GB RAM, 20GB SSD storage
- Registered Domain Name pointing to host IP (e.g., `mindweave.example.com`)

### Environment Secrets Setup

Create the production environment file `backend/.env` from the provided template:

```bash
cp backend/.env.example backend/.env
chmod 600 backend/.env
```

Configure the following critical production keys:

```ini
# Application Configuration
PROJECT_NAME="MindWeave AI"
ENVIRONMENT="production"
DEBUG=False
API_V1_STR="/api/v1"

# Production Security Keys (Generate via: openssl rand -hex 32)
SECRET_KEY="<insert-secure-64-character-random-hex-string>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Connection (Container networking)
DATABASE_URL="postgresql+asyncpg://postgres:postgres_secure_prod_password@db:5432/mindweave_ai_prod"

# Google Gemini AI Integrations
GEMINI_API_KEY="<insert-production-google-ai-studio-gemini-key>"
GEMINI_MODEL="gemini-3.6-flash"
```

> [!IMPORTANT]
> Never commit `backend/.env` or root `.env` to version control. Restrict read permissions to the user running Docker: `chmod 600 backend/.env`.

---

## 3. Stack Deployment & Startup Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/mindweave-ai.git /opt/mindweave-ai
cd /opt/mindweave-ai
```

### Step 2: Build & Start Production Containers
```bash
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Step 3: Verify Automated Alembic Migrations
The backend entrypoint (`backend/entrypoint.sh`) executes `alembic upgrade head` before Uvicorn starts. Check logs to confirm:

```bash
docker compose -f docker-compose.prod.yml logs backend
```

Expected output:
```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade e1a42f567c89 -> f3a1b2c4d5e6, add_documents_and_pgvector_chunks
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Healthcheck Validation
Run healthcheck probes:

```bash
# Liveness probe
curl -I http://localhost:80/api/v1/health

# Readiness probe (verifies database pool and pgvector connectivity)
curl -s http://localhost:80/api/v1/health/ready | jq
```

Expected readiness response:
```json
{
  "status": "ready",
  "database": "connected",
  "latency_ms": 1.45
}
```

---

## 4. SSL/TLS Certificate Setup with Let's Encrypt

To terminate SSL/TLS at Nginx using Let's Encrypt certificates:

### Step 1: Install Certbot on Host
```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

### Step 2: Obtain Certificate
Temporarily stop frontend port 80 or run standalone certbot:
```bash
sudo certbot certonly --standalone -d mindweave.example.com --email ops@example.com --agree-tos --no-eff-email
```

### Step 3: Mount Certificates into Nginx
In `docker-compose.prod.yml`, add certificate volume mounts under `services.frontend`:

```yaml
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
```

### Step 4: Enable HTTPS in `frontend/nginx.conf`
```nginx
server {
    listen 80;
    server_name mindweave.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mindweave.example.com;

    ssl_certificate /etc/letsencrypt/live/mindweave.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mindweave.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 5: Automate Renewal
Add a systemd timer or cron job for auto-renewal:
```bash
0 3 * * * certbot renew --quiet && docker compose -f /opt/mindweave-ai/docker-compose.prod.yml exec frontend nginx -s reload
```

---

## 5. PostgreSQL Backup & Restore Procedures (Handling pgvector)

PostgreSQL contains user accounts, workspaces, mindmaps, nodes, edges, documents, and 768-dimensional `pgvector` chunks. Backups must preserve custom extensions and binary vector encodings.

### Performing a Full Database Backup

Run `pg_dump` with custom binary format (`-Fc`) directly from the database container:

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/mindweave-ai/backups"
mkdir -p "$BACKUP_DIR"

docker compose -f docker-compose.prod.yml exec -T db pg_dump \
    -U postgres \
    -d mindweave_ai_prod \
    -Fc > "$BACKUP_DIR/mindweave_ai_backup_${TIMESTAMP}.dump"

echo "Backup created at: $BACKUP_DIR/mindweave_ai_backup_${TIMESTAMP}.dump"
```

### Automated Nightly Backup Cron Job
Add to `/etc/cron.d/mindweave-backup`:

```bash
# Nightly backup at 02:00 UTC with 14-day retention
0 2 * * * root /usr/local/bin/mindweave-backup.sh >> /var/log/mindweave-backup.log 2>&1
```

Script `/usr/local/bin/mindweave-backup.sh`:
```bash
#!/usr/bin/env bash
set -eo pipefail
BACKUP_DIR="/opt/mindweave-ai/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

docker compose -f /opt/mindweave-ai/docker-compose.prod.yml exec -T db pg_dump \
    -U postgres -d mindweave_ai_prod -Fc > "$BACKUP_DIR/backup_${TIMESTAMP}.dump"

# Delete dumps older than 14 days
find "$BACKUP_DIR" -type f -name "backup_*.dump" -mtime +14 -delete
```

### Restoring from Backup

To restore to a fresh or recovered database:

```bash
# 1. Stop backend services to terminate active pool connections
docker compose -f docker-compose.prod.yml stop backend

# 2. Re-create target database (or drop existing tables)
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS mindweave_ai_prod;"
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -c "CREATE DATABASE mindweave_ai_prod;"
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d mindweave_ai_prod -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 3. Restore schema, tables, and vector embeddings
docker compose -f docker-compose.prod.yml exec -T db pg_restore \
    -U postgres \
    -d mindweave_ai_prod \
    --no-owner \
    --role=postgres \
    < "/opt/mindweave-ai/backups/backup_20261120_120000.dump"

# 4. Restart backend
docker compose -f docker-compose.prod.yml start backend
```

---

## 6. Zero-Downtime Re-deployments & Rolling Updates

To deploy new releases without dropping active user sessions:

```bash
# Step 1: Pull latest changes
git pull origin main

# Step 2: Build new images in background
docker compose -f docker-compose.prod.yml build backend frontend

# Step 3: Rolling update backend container
docker compose -f docker-compose.prod.yml up -d --no-deps backend

# Step 4: Verify health
docker compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/api/v1/health/ready

# Step 5: Rolling update frontend container
docker compose -f docker-compose.prod.yml up -d --no-deps frontend
```

---

## 7. Troubleshooting & Disaster Recovery Runbook

### Issue 1: Backend Container Fails Healthcheck (`unhealthy`)
- **Symptom**: `docker compose ps` shows `mindweave_backend_prod (unhealthy)`.
- **Diagnosis**: Check container logs:
  ```bash
  docker compose -f docker-compose.prod.yml logs --tail=100 backend
  ```
- **Remediation**:
  1. Check database connectivity: `docker compose exec db pg_isready -U postgres`.
  2. If `Missing key inputs argument!`: verify `backend/.env` exists and contains non-empty `GEMINI_API_KEY`.
  3. If migrations failed: check `alembic current` and resolve pending migration head conflicts.

### Issue 2: PostgreSQL Out of Connections (`too many connections`)
- **Symptom**: API endpoints return 500 with `asyncpg.exceptions.TooManyConnectionsError`.
- **Remediation**:
  1. Inspect active connections:
     ```sql
     SELECT count(*), state FROM pg_stat_activity GROUP BY state;
     ```
  2. Increase `max_connections` in Postgres config or tune SQLAlchemy pool size in `backend/app/core/database.py` (`pool_size=20`, `max_overflow=10`).

### Issue 3: Gemini API Quota or 402 Resource Exhausted
- **Symptom**: Log warnings: `RESOURCE_EXHAUSTED` or `402 prepayment depleted`.
- **Behavior**: The built-in development fallback in `MindmapGenerationService` and `NodeExplanationService` engages automatically to synthesize high-fidelity mindmaps and node explanations without interrupting user experience.
- **Remediation**: Replenish API credits in Google AI Studio / Google Cloud Console.

### Issue 4: Corrupted pgvector Extension or Missing DDL
- **Symptom**: Error: `type "vector" does not exist`.
- **Remediation**:
  ```bash
  docker compose -f docker-compose.prod.yml exec db psql -U postgres -d mindweave_ai_prod -c "CREATE EXTENSION IF NOT EXISTS vector;"
  ```
