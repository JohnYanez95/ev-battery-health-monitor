# Docker Setup Guide for EV Battery Health Monitor

This guide covers the complete Docker setup process for the PostgreSQL/TimescaleDB database used in the EV Battery Health Monitor project.

## 📋 Overview

The project uses Docker Compose to run a PostgreSQL database with TimescaleDB extension for time-series data storage. This setup provides:
- **PostgreSQL 14.17** as the base database
- **TimescaleDB 2.19.3** extension for time-series optimization
- **Secure environment variable configuration**
- **Localhost-only access** for security
- **Automatic performance tuning**

---

## 🔧 Prerequisites

Before starting, ensure you have:
- Docker Desktop installed and running
- WSL2 integration enabled (if on Windows)
- Project cloned to `~/Repos/ev-battery-health-monitor/`

---

## 📝 Step-by-Step Setup

### Step 1: Environment Configuration

**Create Environment Variables File**

Navigate to your project directory and create the `.env` file:

```bash
cd ~/Repos/ev-battery-health-monitor
```

Create `.env` with secure configuration:
```bash
# Database Configuration
POSTGRES_DB=battery_health
POSTGRES_USER=ev_monitor_user
POSTGRES_PASSWORD=secure_battery_monitor_2024!

# Application Configuration
APP_ENV=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
```

⚠️ **Important**: The `.env` file is excluded from version control via `.gitignore` for security.

### Step 2: Docker Compose Configuration

The `docker-compose.yml` file should already exist with this secure configuration:

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg14
    container_name: ev-battery-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-battery_health}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    ports:
      - "127.0.0.1:5432:5432"  # Bind only to localhost for security
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: postgres -c shared_preload_libraries=timescaledb
    restart: unless-stopped

volumes:
  postgres_data:
```

### Step 3: Start the Database

**Launch PostgreSQL with TimescaleDB:**

```bash
docker-compose up -d postgres
```

**What happens during startup:**
1. **Image Download**: Downloads TimescaleDB Docker image (if not cached)
2. **Volume Creation**: Creates persistent data volume
3. **Database Initialization**: 
   - Creates database specified in `POSTGRES_DB`
   - Creates superuser specified in `POSTGRES_USER`
   - Installs TimescaleDB extension
   - Runs performance tuning
4. **Container Start**: Database becomes ready for connections

**Expected Output:**
```
[+] Running 3/3
 ✔ Network ev-battery-health-monitor_default         Created
 ✔ Volume "ev-battery-health-monitor_postgres_data"  Created  
 ✔ Container ev-battery-postgres                     Started
```

### Step 4: Verify Database Connection

**Check Container Status:**
```bash
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                               PORTS                      NAMES
xxxxxxxxxx     timescale/timescaledb:latest-pg14   127.0.0.1:5432->5432/tcp   ev-battery-postgres
```

**Test Database Connection:**
```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "SELECT current_user;"
```

Expected output:
```
  current_user   
-----------------
 ev_monitor_user
(1 row)
```

### Step 5: Verify TimescaleDB Extension

**Check PostgreSQL Version:**
```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "SELECT version();"
```

**Verify TimescaleDB Extension:**
```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';"
```

Expected output:
```
   extname   | extversion 
-------------+------------
 timescaledb | 2.19.3
(1 row)
```

---

## ⚠️ Important Notes

### Superuser Behavior

**Key Understanding**: The `POSTGRES_USER` environment variable determines the database superuser, NOT just a regular user.

- **Environment Variable**: `POSTGRES_USER=ev_monitor_user`
- **Result**: `ev_monitor_user` becomes the database superuser
- **No Default**: The traditional `postgres` user is NOT created

This is different from many tutorials that assume a `postgres` superuser exists. Our configuration creates `ev_monitor_user` as the superuser directly.

### Security Configuration

**Localhost Binding**: 
- Port mapping: `127.0.0.1:5432:5432`
- Database only accessible from local machine
- No external network access allowed

**Environment Variables**:
- Credentials stored in `.env` file
- Not hardcoded in docker-compose.yml
- Excluded from version control

### Performance Tuning

TimescaleDB automatically tunes PostgreSQL settings based on your system:
- **Memory allocation** optimized for available RAM
- **Worker processes** scaled to CPU count
- **Connection limits** set appropriately
- **Background workers** configured for TimescaleDB

---

## 🔍 Troubleshooting

### Container Won't Start

**Check Docker Desktop is running:**
```bash
docker --version
```

**View container logs:**
```bash
docker logs ev-battery-postgres
```

**Restart container:**
```bash
docker-compose down
docker-compose up -d postgres
```

### Connection Refused

**Wait for initialization**: Database may still be starting up. Check logs:
```bash
docker logs ev-battery-postgres | tail -10
```

Look for: `database system is ready to accept connections`

**Check port binding:**
```bash
docker port ev-battery-postgres
```

Should show: `5432/tcp -> 127.0.0.1:5432`

### Permission Issues

**Volume permissions**: If you encounter permission issues:
```bash
docker-compose down
docker volume rm ev-battery-health-monitor_postgres_data
docker-compose up -d postgres
```

### TimescaleDB Extension Issues

**Manual extension creation** (shouldn't be needed, but just in case):
```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Environment Variable Issues

**Check environment loading:**
```bash
docker exec ev-battery-postgres env | grep POSTGRES
```

**Verify .env file exists:**
```bash
ls -la .env
```

---

## 🧪 Testing Database Functionality

### Create Test Hypertable

Test TimescaleDB functionality by creating a sample hypertable:

```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "
CREATE TABLE IF NOT EXISTS test_telemetry (
    time TIMESTAMPTZ NOT NULL,
    vehicle_id TEXT NOT NULL,
    soc_percent REAL,
    voltage REAL,
    current REAL,
    temperature REAL
);
SELECT create_hypertable('test_telemetry', 'time', if_not_exists => TRUE);
"
```

**Clean up test table:**
```bash
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "DROP TABLE IF EXISTS test_telemetry;"
```

### Interactive Database Session

For exploratory work, connect interactively:
```bash
docker exec -it ev-battery-postgres psql -U ev_monitor_user -d battery_health
```

**Note**: This requires a TTY. In non-interactive environments, use the `-c` flag to execute specific commands.

---

## 🚀 Next Steps

Once your database is running successfully:

1. **Verify all tests pass** using the commands above
2. **Proceed to Phase 1**: Data Simulation Engine development
3. **Create time-series schemas** for EV battery telemetry
4. **Implement data ingestion** using TimescaleDB best practices

---

## 🔧 Useful Commands

### Container Management
```bash
# Start database
docker-compose up -d postgres

# Stop database
docker-compose down

# View logs
docker logs ev-battery-postgres

# Container stats
docker stats ev-battery-postgres
```

### Database Operations
```bash
# Execute single command
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "COMMAND"

# Interactive session (requires TTY)
docker exec -it ev-battery-postgres psql -U ev_monitor_user -d battery_health

# Check connection readiness
docker exec ev-battery-postgres pg_isready -U ev_monitor_user
```

### System Information
```bash
# Check container details
docker inspect ev-battery-postgres

# View port mappings
docker port ev-battery-postgres

# List volumes
docker volume ls
```

---

## 📚 Additional Resources

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [TimescaleDB Docker Image](https://hub.docker.com/r/timescale/timescaledb)

---

**✅ Database Setup Complete**: Your PostgreSQL/TimescaleDB environment is now ready for EV battery telemetry data!