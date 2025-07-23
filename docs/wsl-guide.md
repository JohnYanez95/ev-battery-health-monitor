# WSL2 Setup Guide for EV Battery Health Monitor

## Overview

This comprehensive guide walks you through setting up Windows Subsystem for Linux 2 (WSL2) for the EV Battery Health Monitor project, including all the real-world troubleshooting you'll likely encounter. WSL2 provides a native Linux environment on Windows, making it ideal for full-stack development with better Docker integration and simpler dependency management.

## Why WSL2 for This Project

- **Consistent Environment**: Same Node.js/Python versions across development and production
- **Better Docker Integration**: Native Linux container support for PostgreSQL/TimescaleDB
- **Simplified Path Handling**: No Windows/Linux path translation issues
- **Package Management**: Native Linux package managers (apt)
- **Development Tools**: Better terminal, shell scripting, and CLI tools

---

## Part I: Initial Setup

### Prerequisites

- Windows 10 version 2004+ or Windows 11
- Administrator access
- At least 8GB free disk space (for full stack + Docker)

### 1. Install WSL2 with Ubuntu

```cmd
# In PowerShell (as Administrator)
wsl --install Ubuntu-22.04
wsl --set-default-version 2
```

**What happens:**
- Downloads and installs WSL2 kernel
- Installs Ubuntu 22.04 LTS distribution
- Sets WSL2 as default version

### 2. Initial Ubuntu Setup

After installation, Ubuntu will prompt for:
- **Username**: Create a UNIX username (doesn't need to match Windows username)
- **Password**: Set a password for sudo commands

**Important WSL Nuances:**
- WSL may start in Windows directories (`/mnt/c/...`) - use `cd ~` to get to Linux home
- Start WSL properly with `wsl ~` (not just `wsl`) to begin in home directory
- Use Windows Terminal for better WSL integration
- Multi-line command pasting works seamlessly

### 3. System Updates

```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y
```

### 4. Install Development Dependencies

#### Node.js 18+ Installation (Required for Frontend)

**⚠️ Critical**: Ubuntu 22.04's default Node.js (v12.22.9) is incompatible with modern React/Next.js development.

```bash
# Install current Node.js LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Configure npm global directory
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### Python 3.10+ Installation (Required for Backend)

```bash
# Install Python 3.10 and development tools
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Create python3 alias for consistency
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

**Note**: Ubuntu 22.04 comes with Python 3.10.12 which is perfect for FastAPI development

#### PostgreSQL Client Tools

```bash
# Install PostgreSQL client for database management
sudo apt install -y postgresql-client
```

### 5. Configure Git

```bash
# Configure git (replace with your information)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main

# Optional: Cache credentials
git config --global credential.helper store
```

### 6. Clone Project and Setup Development Environment

```bash
# Create Repos directory and clone project
mkdir -p ~/Repos
cd ~/Repos
git clone https://github.com/yourusername/ev-battery-health-monitor.git
cd ev-battery-health-monitor

# Create backend virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 7. Docker Installation

**Recommended: Docker Desktop**

Docker Desktop is preferred for Windows developers because:
- Single installation works across Windows and WSL
- GUI management interface for PostgreSQL containers
- Automatic WSL2 integration
- Better resource management for TimescaleDB

**Setup Steps:**
1. Download and install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. In Docker Desktop settings, go to **Resources** → **WSL Integration**
3. Enable integration with Ubuntu-22.04
4. Apply & Restart Docker Desktop
5. Restart WSL session: `exit` then `wsl ~`
6. Test in WSL: `docker --version`

**Container Access from Windows Browser:**
When running containers in WSL, use `http://127.0.0.1:PORT` instead of `http://localhost:PORT` to access them from Windows browsers. The `localhost` resolution sometimes fails in the WSL-Windows bridge, while `127.0.0.1` works reliably.

### 8. Database Setup with Docker

For the EV Battery Health Monitor project, we use Docker to run PostgreSQL with TimescaleDB extension for time-series data storage.

**📖 Complete Setup Guide**: For detailed Docker setup instructions, troubleshooting, and advanced configuration, see our comprehensive **[Docker Setup Guide](docker-guide.md)**.

#### Quick Setup

**Prerequisites**: Ensure Docker Desktop is running and integrated with WSL2.

**Step 1: Navigate to project directory**
```bash
cd ~/Repos/ev-battery-health-monitor
```

**Step 2: Environment Configuration**
The project includes `.env.example` as a template. Copy and customize it:
```bash
cp .env.example .env
# Edit .env with your secure configuration
```

**Step 3: Start Database**
```bash
# Start PostgreSQL with TimescaleDB
docker-compose up -d postgres

# Wait for initialization (check logs if needed)
docker logs ev-battery-postgres

# Test connection
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "SELECT current_user;"
```

#### Important Notes

**Superuser Configuration**: 
- The `POSTGRES_USER` environment variable creates the database superuser
- With `POSTGRES_USER=ev_monitor_user`, this user becomes the superuser (not `postgres`)
- This is the correct behavior for our secure configuration

**Security Features**:
- Database only accessible via `127.0.0.1:5432` (localhost only)
- Credentials stored in `.env` file (excluded from version control)
- Automatic performance tuning by TimescaleDB

**For detailed troubleshooting, testing procedures, and advanced configuration, refer to the [Docker Setup Guide](docker-guide.md).**

---

## Part II: Installing Claude Code

### Claude Code Installation

```bash
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code
```

**Verify Installation:**
```bash
node --version  # Should show v18+ or v20+
claude --version
```

---

## Part III: Troubleshooting

### VPN and Claude Code Connectivity Issues

#### Problem 1: Basic VPN Blocking

**Symptoms**: Claude Code shows "offline mode" when VPN is active

**Solution**: Configure VPN split tunneling

**For NordVPN:**
1. **Enable Split Tunneling** in VPN settings
2. **Select "Bypass VPN for selected apps"**
3. **Add these applications**:
   - `powershell.exe` (`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`)
   - `wsl.exe` (`C:\Windows\System32\wsl.exe`)

**Test procedure:**
1. Configure split tunneling
2. Close PowerShell completely and open a new one
3. Run `wsl ~`
4. Test: `claude --version`

#### Problem 2: IPv6 Black-hole Issue

**Symptoms**: Even with split tunneling, Claude Code timeouts when connecting

**Root Cause**: VPN providers often don't support IPv6, creating a black-hole where WSL tries IPv6 first (times out), before falling back to IPv4.

**Solution: Disable IPv6 in WSL**

```bash
# Test if IPv6 is the issue (should timeout with VPN on)
curl -6 --connect-timeout 5 https://api.anthropic.com

# Disable IPv6 immediately
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1

# Make persistent across reboots
echo 'net.ipv6.conf.all.disable_ipv6=1' | sudo tee /etc/sysctl.d/99-disable-ipv6.conf
echo 'net.ipv6.conf.default.disable_ipv6=1' | sudo tee -a /etc/sysctl.d/99-disable-ipv6.conf

# Restart WSL
exit
```

In PowerShell:
```cmd
wsl --shutdown
wsl ~
```

**Verification:**
```bash
claude --version  # Should connect immediately
```

### Node.js Installation Issues

#### Problem: Package Conflicts

**Symptoms:**
```
dpkg: error processing archive ... trying to overwrite '/usr/include/node/common.gypi', 
which is also in package libnode-dev
```

**Solution: Complete Clean Removal**
```bash
# Remove all conflicting packages
sudo apt purge -y nodejs npm libnode*
sudo apt autoremove -y
sudo apt clean
sudo apt update --fix-missing

# Install via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Configure and install Claude Code
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g @anthropic-ai/claude-code
```

### Docker and Database Issues

#### Problem: PostgreSQL Connection Refused

**Symptoms**: Backend can't connect to PostgreSQL container

**Solutions:**
```bash
# Check if containers are running
docker ps

# Restart Docker Compose services
docker-compose down
docker-compose up -d

# Check PostgreSQL logs
docker-compose logs postgres
```

#### Problem: TimescaleDB Extension Issues

**Symptoms**: TimescaleDB functions not available

**Solution:**
```bash
# Connect to database and enable extension
docker exec -it ev-battery-postgres psql -U ev_monitor_user -d battery_health
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### GitHub Authentication

**Important**: GitHub no longer accepts passwords - use Personal Access Tokens (PAT):

1. **Create PAT**: GitHub.com → Profile → Settings → Developer settings → Personal access tokens → Generate new token
2. **Scopes**: Check `repo` for full repository access
3. **Usage**: When Git prompts for password, paste your PAT token
4. **Credential Caching**: With `git config --global credential.helper store`, Git saves PAT after first use

---

## Part IV: Development Workflow

### Starting the Development Environment

```bash
# Start database services
docker-compose up -d postgres

# Start backend (in new terminal)
cd ~/Repos/ev-battery-health-monitor/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd ~/Repos/ev-battery-health-monitor/frontend
npm run dev
```

### Environment Verification

```bash
# Check Node.js version
node --version
# Expected: v18+ or v20+

# Check Python version  
python3 --version
# Expected: Python 3.10.12

# Check Docker
docker --version

# Check Claude Code
claude --version

# Test database connection
docker exec ev-battery-postgres pg_isready -U ev_monitor_user
```

### VS Code Integration

1. **Install Extensions**:
   - WSL (ms-vscode-remote.remote-wsl)
   - Remote Development extension pack
   - Python extension
   - ES7+ React/Redux/React-Native snippets

2. **Connect to WSL**:
   ```bash
   cd ~/Repos/ev-battery-health-monitor
   code .
   ```

3. **Configure Python Environment**:
   - Install Python extension in WSL context
   - Select interpreter: `~/Repos/ev-battery-health-monitor/backend/venv/bin/python`

---

## Setup Completion Checklist

- [ ] WSL2 with Ubuntu 22.04 installed
- [ ] Node.js v18+ available (`node --version`)
- [ ] Python 3.10+ available (`python3 --version`)
- [ ] Git configured with name/email
- [ ] Project cloned to `~/Repos/ev-battery-health-monitor/`
- [ ] Backend virtual environment created (`backend/venv/`)
- [ ] Frontend dependencies installed (`node_modules/`)
- [ ] Docker Desktop integrated with WSL
- [ ] PostgreSQL container running (`docker ps`)
- [ ] Claude Code installed and connecting (`claude --version`)
- [ ] VPN connectivity issues resolved (if applicable)
- [ ] VS Code WSL integration working

---

## File System Navigation

**Key Paths:**
- Linux home: `~/` or `/home/username/`
- Windows files: `/mnt/c/Users/Username/`
- Project location: `~/Repos/ev-battery-health-monitor/`

**Performance Tips:**
- Keep project files in WSL filesystem (`~/`) for better performance
- Use WSL2 for Docker compatibility
- Close unused WSL distributions: `wsl --shutdown`

---

## Development Command Reference

### Frontend Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `npm run dev` | Start development server | `cd frontend && npm run dev` |
| `npm run build` | Build for production | `npm run build` |
| `npm run lint` | Run ESLint | `npm run lint` |
| `npm install` | Install dependencies | `npm install package-name` |

### Backend Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `uvicorn main:app --reload` | Start FastAPI server | In backend/ with venv active |
| `pip install` | Install Python packages | `pip install package-name` |
| `alembic upgrade head` | Run database migrations | Database schema updates |
| `pytest` | Run tests | `pytest tests/` |

### Docker Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `docker-compose up -d` | Start services in background | `docker-compose up -d postgres` |
| `docker-compose down` | Stop services | `docker-compose down` |
| `docker-compose logs` | View service logs | `docker-compose logs postgres` |
| `docker exec -it` | Connect to container | Connect to running database |

---

**🎉 Congratulations!** Your WSL2 development environment is now ready for the EV Battery Health Monitor project. You have a robust, full-stack development setup that handles the complexities of React/FastAPI/PostgreSQL development while maintaining compatibility with your Windows workflow.