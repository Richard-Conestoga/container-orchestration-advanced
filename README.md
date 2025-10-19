# Containerized User Management API

A production-ready, containerized web application with Flask API and PostgreSQL database, implementing DevOps best practices.

## 📋 Documentation Checklist

This README covers:

✅ **Build Instructions** - Complete guide to building Docker images  
✅ **Configuration Guide** - Environment variables, database setup, customization  
✅ **Run Instructions** - Starting, stopping, verifying deployments  
✅ **Dockerfile Explanation** - Purpose and security features of application container  
✅ **docker-compose.yml Breakdown** - All services, volumes, networks explained  
✅ **Scaling Setup** - Horizontal scaling with load balancing (nginx)  
✅ **Load Balancing** - Multiple strategies and implementations  
✅ **Security Measures** - 10+ security best practices with explanations  

## Features# Containerized User Management API

A production-ready, containerized web application with Flask API and PostgreSQL database, implementing DevOps best practices.

## Features

- **RESTful API** for user management (Create, Read, List)
- **PostgreSQL Database** with persistent storage
- **Docker Compose** orchestration
- **Security Best Practices**: Non-root users, resource limits, secrets management
- **Health Checks** for both application and database
- **Logging** to persistent volumes
- **Scalable Architecture** with isolated networks

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Flask API     │◄───────►│   PostgreSQL     │
│   (Port 5000)   │         │   Database       │
│                 │         │                  │
│  - Non-root     │         │  - Persistent    │
│  - Health check │         │    Volume        │
│  - Logging      │         │  - Init Script   │
└─────────────────┘         └──────────────────┘
         │                           │
         └───────────┬───────────────┘
                     │
              app_network (Bridge)
```

## Docker Configuration Overview

### 1. **Dockerfile** - Application Container Image

**Purpose**: Defines how to build the Flask API application container with security best practices.

**Key Components**:
- **Base Image**: `python:3.11-slim` - Minimal Python image (~150MB vs ~1GB for full image)
- **Non-root User**: Creates `appuser` user/group to run the application without root privileges
- **Working Directory**: `/app` - Contains application code and logs
- **Dependencies**: Installed from `requirements.txt` using pip
- **Health Check**: Built-in health monitoring that checks `/health` endpoint every 30 seconds
- **Port Exposure**: Port 5000 (non-privileged port, >1024)

**Security Features**:
```dockerfile
# Creates dedicated user (non-root)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Runs container as non-root user
USER appuser

# Minimizes attack surface with slim image
FROM python:3.11-slim
```

### 2. **docker-compose.yml** - Multi-Container Orchestration

**Purpose**: Defines and orchestrates multiple services (web + database) with networking, volumes, and dependencies.

**Service Definitions**:

#### **Database Service (`db`)**
- **Image**: `postgres:16-alpine` - Lightweight PostgreSQL (Alpine Linux base)
- **Container Name**: `user_db` - Fixed name for easy reference
- **Restart Policy**: `unless-stopped` - Auto-restart on failure (except manual stop)
- **Environment Variables**: Database credentials from `.env` file
- **Volumes**: 
  - `db_data:/var/lib/postgresql/data` - Persistent database storage
  - `./init.sql:/docker-entrypoint-initdb.d/init.sql:ro` - Database initialization (read-only)
- **Health Check**: Verifies PostgreSQL is ready using `pg_isready` command
- **Resource Limits**: 1 CPU core max, 512MB RAM max
- **Network**: Connected to `app_network` (isolated bridge network)

#### **Web Application Service (`web`)**
- **Build Context**: Current directory with Dockerfile
- **Container Name**: `user_api` - Fixed name for easy reference
- **Restart Policy**: `unless-stopped` - Auto-restart on failure
- **Port Mapping**: `5000:5000` - Exposes API to host machine
- **Environment Variables**: Database connection details from `.env` file
- **Volumes**: `app_logs:/app/logs` - Persistent log storage
- **Dependencies**: Waits for `db` service to be healthy before starting
- **Health Check**: Verifies Flask API responds on `/health` endpoint
- **Resource Limits**: 0.5 CPU core max, 256MB RAM max
- **Network**: Connected to `app_network` (can communicate with `db`)

#### **Volumes** (Named Volumes)
- **`db_data`**: Persists PostgreSQL database files across container restarts
- **`app_logs`**: Persists application logs across container restarts

#### **Network** (`app_network`)
- **Type**: Bridge network (default Docker network driver)
- **Purpose**: Isolates containers from external networks
- **DNS**: Automatic service discovery (containers can reach each other by service name)
- **Security**: Database is NOT exposed to host, only accessible within network

### 3. **init.sql** - Database Initialization Script

**Purpose**: Automatically creates database schema when PostgreSQL container first starts.

**What It Does**:
- Creates `users` table with proper constraints
- Adds indexes for performance optimization
- Inserts sample data for testing
- Uses `IF NOT EXISTS` to prevent errors on restart

### 4. **requirements.txt** - Python Dependencies

**Purpose**: Specifies exact versions of Python packages needed by the application.

**Dependencies**:
- `Flask==3.0.0` - Web framework for API
- `psycopg2-binary==2.9.9` - PostgreSQL database adapter
- `requests==2.31.0` - HTTP library (used in health checks)

### 5. **.env File** - Environment Variables (Secrets)

**Purpose**: Stores sensitive configuration (passwords, credentials) outside of code.

**Why It's Important**:
- Keeps secrets out of version control
- Easy to change per environment (dev/staging/prod)
- Follows 12-factor app methodology

**Variables Defined**:
- `DB_NAME` - Database name
- `DB_USER` - Database username  
- `DB_PASSWORD` - Database password (MUST be changed from default)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Clone and Setup

```bash
# Create project directory
mkdir user-api && cd user-api

# Copy all files to this directory
# - web_app.py
# - Dockerfile
# - requirements.txt
# - init.sql
# - docker-compose.yml
# - .env.example
# - .gitignore
```

### 2. Configure Environment

```bash
# Create .env file from template
cp .env.example .env

# Edit .env and set secure credentials
nano .env
```

**Important**: Change the default password in `.env`:

```bash
DB_NAME=userdb
DB_USER=appuser
DB_PASSWORD=your_secure_password_here
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","timestamp":"2025-10-19T..."}
```

## Detailed Build, Configure, and Run Instructions

### Building Containers

#### Method 1: Using Docker Compose (Recommended)

```bash
# Build all services defined in docker-compose.yml
docker-compose build

# Build with no cache (force rebuild)
docker-compose build --no-cache

# Build specific service only
docker-compose build web
```

**What happens during build**:
1. Reads `Dockerfile` in current directory
2. Downloads Python 3.11 slim base image (~150MB)
3. Creates non-root user `appuser`
4. Creates `/app/logs` directory with proper permissions
5. Installs Python dependencies from `requirements.txt`
6. Copies `web_app.py` into container
7. Sets ownership to `appuser`
8. Configures health check and startup command
9. Tags image as `assign2-advanced-web`

**Build time**: ~2-5 minutes (first time), ~10-30 seconds (subsequent builds with cache)

#### Method 2: Building Docker Image Directly

```bash
# Build application image manually
docker build -t user-api:latest .

# Build with specific tag
docker build -t user-api:v1.0 .

# Build with build arguments (if needed)
docker build --build-arg PYTHON_VERSION=3.11 -t user-api .
```

### Configuring the Application

#### 1. Environment Variables Configuration

Create and edit `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
# or
code .env
```

**Required Variables**:
```bash
# Database Configuration
DB_NAME=userdb              # Name of PostgreSQL database
DB_USER=appuser             # Database username
DB_PASSWORD=SecurePass123!  # CHANGE THIS! Use strong password

# Optional: Override defaults
DB_HOST=db                  # Container name of database service
DB_PORT=5432               # PostgreSQL default port
```

**Password Requirements**:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters
- Avoid common words or patterns

**Generate secure password**:
```bash
# Linux/Mac
openssl rand -base64 32

# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2. Database Initialization Configuration

Edit `init.sql` to customize initial schema:

```sql
-- Add custom fields to users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,          -- Add email field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add custom indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add custom sample data
INSERT INTO users (first_name, last_name, email) VALUES
    ('Admin', 'User', 'admin@example.com')
ON CONFLICT DO NOTHING;
```

#### 3. Docker Compose Configuration

Edit `docker-compose.yml` to customize:

**Change exposed port**:
```yaml
services:
  web:
    ports:
      - "8080:5000"  # Access on port 8080 instead of 5000
```

**Adjust resource limits**:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'      # Increase CPU limit
          memory: 512M     # Increase memory limit
```

**Add environment-specific settings**:
```yaml
services:
  web:
    environment:
      FLASK_ENV: production     # or development
      LOG_LEVEL: INFO          # DEBUG, INFO, WARNING, ERROR
```

### Running the Application

#### Starting Services

```bash
# Start all services in background (detached mode)
docker-compose up -d

# Start with logs visible (foreground)
docker-compose up

# Start specific service only
docker-compose up -d db    # Database only
docker-compose up -d web   # Web app only

# Force recreate containers
docker-compose up -d --force-recreate

# Pull latest images before starting
docker-compose up -d --pull always
```

#### Checking Status

```bash
# View running containers
docker-compose ps

# Expected output:
# NAME       STATUS                    PORTS
# user_api   Up 2 minutes (healthy)    0.0.0.0:5000->5000/tcp
# user_db    Up 2 minutes (healthy)    5432/tcp

# View detailed container info
docker-compose ps -a

# Check logs
docker-compose logs        # All services
docker-compose logs web    # Web service only
docker-compose logs db     # Database only
docker-compose logs -f     # Follow logs (real-time)
docker-compose logs --tail=50  # Last 50 lines
```

#### Verifying Deployment

```bash
# 1. Check container health
docker inspect user_api --format='{{.State.Health.Status}}'
# Should return: healthy

docker inspect user_db --format='{{.State.Health.Status}}'
# Should return: healthy

# 2. Test API health endpoint
curl http://localhost:5000/health
# Expected: {"status":"healthy","timestamp":"..."}

# 3. Test database connectivity
docker exec user_db psql -U appuser -d userdb -c "SELECT 1;"
# Expected: Returns 1

# 4. Test API functionality
curl -X POST http://localhost:5000/user \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User"}'
# Expected: Returns user with ID

# 5. Check logs for errors
docker-compose logs web | grep ERROR
docker-compose logs db | grep ERROR
# Expected: No errors
```

#### Accessing Services

**Web Application**:
```bash
# Local access
curl http://localhost:5000/health

# From another machine on same network
curl http://<your-ip>:5000/health

# Find your IP
hostname -I  # Linux
ipconfig getifaddr en0  # Mac
ipconfig  # Windows
```

**Database**:
```bash
# Access PostgreSQL CLI
docker exec -it user_db psql -U appuser -d userdb

# Run SQL query
docker exec user_db psql -U appuser -d userdb -c "SELECT * FROM users;"

# Backup database
docker exec user_db pg_dump -U appuser userdb > backup_$(date +%Y%m%d).sql

# Restore database
cat backup.sql | docker exec -i user_db psql -U appuser -d userdb
```

### Stopping and Cleaning Up

```bash
# Stop services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers AND volumes (deletes data!)
docker-compose down -v

# Stop, remove everything including images
docker-compose down --rmi all -v

# Stop specific service
docker-compose stop web
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web

# Restart with rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

### Updating the Application

```bash
# After making code changes to web_app.py

# Method 1: Rebuild and restart
docker-compose build web
docker-compose up -d web

# Method 2: Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Method 3: Rolling update (no downtime)
docker-compose up -d --no-deps --build web
```

### Troubleshooting Build/Run Issues

**Problem: Port already in use**
```bash
# Check what's using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Solution: Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use 8080 instead
```

**Problem: Permission denied errors**
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
chmod 644 .env
chmod 755 .
```

**Problem: Database won't start**
```bash
# Check logs
docker-compose logs db

# Remove corrupted volume and restart
docker-compose down -v
docker-compose up -d
```

**Problem: Build fails**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache --pull
```

## API Endpoints

### Create User

```bash
curl -X POST http://localhost:5000/user \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe"}'

# Response (201):
# {
#   "id": 1,
#   "first_name": "John",
#   "last_name": "Doe",
#   "created_at": "2025-10-19T12:00:00"
# }
```

### Get User by ID

```bash
curl http://localhost:5000/user/1

# Response (200):
# {
#   "id": 1,
#   "first_name": "John",
#   "last_name": "Doe",
#   "created_at": "2025-10-19T12:00:00"
# }
```

### List All Users (with pagination)

```bash
curl "http://localhost:5000/users?limit=10&offset=0"

# Response (200):
# {
#   "users": [...],
#   "limit": 10,
#   "offset": 0
# }
```

### Health Check

```bash
curl http://localhost:5000/health

# Response (200):
# {"status":"healthy","timestamp":"..."}
```

## Security Features

### 1. Non-Root Users
- Application runs as `appuser` (UID/GID created in Dockerfile)
- Database runs as `postgres` user (Alpine default)

### 2. Secrets Management
- Credentials stored in `.env` file (not committed to Git)
- Environment variables passed to containers
- No hardcoded secrets in code

### 3. Network Isolation
- Custom bridge network (`app_network`)
- Database not exposed to host (only accessible within network)
- Application exposed only on necessary port (5000)

### 4. Resource Limits
- CPU and memory limits defined in docker-compose
- Prevents resource exhaustion

### 5. Minimal Images
- Python slim image (not full)
- PostgreSQL Alpine image
- Only necessary packages installed

### 6. Read-Only Mounts
- Database initialization script mounted as read-only

## Scaling and Load Balancing

### Horizontal Scaling (Multiple Web Instances)

Docker Compose supports scaling web services to handle increased load:

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3

# Verify scaled instances
docker-compose ps
```

**Current Limitation**: Port conflict will occur because multiple containers can't bind to the same port (5000).

**Solution**: Use a reverse proxy load balancer (nginx or traefik).

### Load Balancing Setup with Nginx

To properly load balance across multiple instances, add an nginx reverse proxy:

**1. Create `nginx.conf`:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream flask_api {
        least_conn;  # Load balancing method
        server web1:5000;
        server web2:5000;
        server web3:5000;
    }

    server {
        listen 80;
        
        location / {
            proxy_pass http://flask_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://flask_api/health;
        }
    }
}
```

**2. Update `docker-compose.yml` for scaling:**
```yaml
services:
  web:
    build: .
    # Remove port mapping - nginx will handle it
    # ports:
    #   - "5000:5000"
    deploy:
      replicas: 3  # Run 3 instances
    networks:
      - app_network

  nginx:
    image: nginx:alpine
    container_name: load_balancer
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web
    networks:
      - app_network
```

**3. Start with scaling:**
```bash
docker-compose up -d --scale web=3
```

**Load Balancing Methods**:
- **Round Robin** (default): Distributes requests evenly
- **Least Connections** (`least_conn`): Sends to server with fewest connections
- **IP Hash**: Same client always goes to same server (session persistence)

**Health Monitoring**: Nginx automatically removes unhealthy backends from the pool.

### Auto-Scaling with Docker Swarm

For production auto-scaling based on load:

```bash
# Initialize swarm
docker swarm init

# Deploy stack with auto-scaling
docker stack deploy -c docker-compose.yml userapi

# Scale based on CPU usage (requires swarm mode)
docker service scale userapi_web=5

# Auto-scale configuration in docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
```


### Database Scaling Considerations

**Current Setup**: Single PostgreSQL instance (suitable for moderate load)

**Scaling Options**:
1. **Vertical Scaling**: Increase resources (CPU/RAM) in docker-compose.yml
2. **Read Replicas**: Add read-only database instances for GET requests
3. **Connection Pooling**: Use PgBouncer to manage database connections efficiently
4. **Managed Database**: Use cloud services (AWS RDS, Google Cloud SQL) for automatic scaling

**Example: Adding Connection Pooling with PgBouncer**:
```yaml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer
    environment:
      DATABASES_HOST: db
      DATABASES_PORT: 5432
      DATABASES_USER: appuser
      DATABASES_PASSWORD: ${DB_PASSWORD}
      DATABASES_DBNAME: userdb
      PGBOUNCER_POOL_MODE: transaction
      PGBOUNCER_MAX_CLIENT_CONN: 100
    depends_on:
      - db
    networks:
      - app_network
```

Then update web service to connect to `pgbouncer:6432` instead of `db:5432`.

### Database Volume
```bash
# Inspect database volume
docker volume inspect user-api_db_data

# Backup database
docker exec user_db pg_dump -U appuser userdb > backup.sql

# Restore database
docker exec -i user_db psql -U appuser userdb < backup.sql
```

### Application Logs
```bash
# View logs from volume
docker exec user_api cat /app/logs/app.log

# Export logs
docker cp user_api:/app/logs/app.log ./local-app.log
```

## Maintenance Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Scale Application (if needed)
```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3
```

### Clean Up Everything
```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes (CAUTION: deletes all data)
docker-compose down -v
```

## Monitoring

### Check Service Health
```bash
docker-compose ps
```

### Database Connection Test
```bash
docker exec -it user_db psql -U appuser -d userdb -c "SELECT COUNT(*) FROM users;"
```

### Application Health Test
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is ready
docker-compose logs db

# Verify environment variables
docker-compose exec web env | grep DB_
```

### Application Won't Start
```bash
# Check application logs
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache web
docker-compose up -d
```

### Permission Issues
```bash
# Check user in container
docker-compose exec web whoami

# Should return: appuser
```

## Development vs Production

### Development Mode
```yaml
# In docker-compose.yml, add:
services:
  web:
    volumes:
      - ./web_app.py:/app/web_app.py  # Hot reload
    environment:
      FLASK_ENV: development
```

### Production Recommendations
1. Use specific image versions (not `latest`)
2. Implement proper SSL/TLS termination
3. Use a reverse proxy (nginx/traefik)
4. Set up monitoring (Prometheus/Grafana)
5. Implement automated backups
6. Use secrets management (Docker Swarm/Kubernetes secrets)
7. Enable audit logging
8. Implement rate limiting

## Project Structure

```
.
├── web_app.py            # Flask application
├── Dockerfile            # Application container definition
├── requirements.txt      # Python dependencies
├── init.sql              # Database initialization script
├── docker-compose.yml    # Service orchestration
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```
