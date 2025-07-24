# EV Battery Health Monitor

A web application for monitoring and labeling electric vehicle battery health events in time series data. Users can visualize battery performance metrics, interactively label anomalous events, and export labeled datasets for machine learning model training.

## 🎯 Overview

This project provides an interactive platform for EV battery data analysis, featuring:
- Real-time battery telemetry visualization
- Interactive time series labeling for anomaly detection
- Export capabilities for ML model training
- Simulated EV battery data generation

## 🔋 Features

- **Interactive Time Series Plots** - Zoom, pan, and explore battery metrics
- **Event Labeling** - Click-and-drag to label thermal events, charging anomalies, etc.
- **Data Simulation** - Generate realistic EV battery performance data
- **Export System** - Output labeled datasets in CSV/JSON format
- **Multi-metric Support** - SoC, voltage, current, temperature, and derived metrics

## 🏗️ Tech Stack

- **Frontend**: React/Next.js with TypeScript
- **Visualization**: Plotly.js for interactive charts
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with TimescaleDB
- **Data Processing**: Pandas, NumPy
- **Deployment**: Docker + Docker Compose

> **📋 Industry Research**: This tech stack was chosen based on comprehensive analysis of current EV battery monitoring industry standards and best practices. See our detailed [Industry Standards Research](research/EV_Battery_Health_Monitor_Industry_Standards.md) for technical justification and market analysis.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/JohnYanez95/ev-battery-health-monitor.git
cd ev-battery-health-monitor

# Set up environment variables
cp .env.example .env
# Edit .env with your secure configuration

# Start the database
docker-compose up -d postgres

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize the database schema
python backend/database/init_db.py

# Install frontend dependencies (when ready)
# cd frontend
# npm install
```

### Security Configuration

This project uses environment variables for secure configuration. The `.env` file contains:
- Database credentials
- Application configuration
- API settings

**Important**: Never commit the `.env` file to version control. Use `.env.example` as a template.

### Development

```bash
# Start the development servers
npm run dev          # Frontend (port 3000)
python -m uvicorn main:app --reload  # Backend (port 8000)
```

## 📊 Data Types

### Primary Metrics
- **State of Charge (SoC)** - Battery level percentage
- **Voltage** - Pack voltage (300-420V)
- **Current** - Charge/discharge current
- **Temperature** - Cell temperature
- **Power** - Instantaneous power

### Event Types
- Thermal events
- Rapid degradation
- Charging anomalies
- Deep discharge events
- Cell imbalance

## 🎯 Use Cases

- **Fleet Management** - Monitor battery health across vehicle fleets
- **Predictive Maintenance** - Identify potential failures before they occur
- **Insurance** - Risk assessment based on battery condition
- **Research** - Generate labeled datasets for ML model development

## 📈 Roadmap

- [x] Project planning and architecture
- [x] Industry standards research and tech stack validation
- [x] Database infrastructure setup (PostgreSQL + TimescaleDB)
- [x] Security configuration and documentation
- [x] Development environment and branch structure
- [ ] **Phase 1: Data simulation engine** ← *Currently developing*
  - [x] TimescaleDB schema with hypertables and compression
  - [x] Database connection pooling module
  - [ ] Battery physics simulation engine
  - [ ] Charging/discharging patterns (CC-CV)
  - [ ] Anomaly generation system
- [ ] Phase 2: Backend API development
- [ ] Phase 3: Frontend & visualization
- [ ] Phase 4: Interactive labeling system
- [ ] Phase 5: Export functionality and deployment

## 📚 Documentation

- **[Industry Standards Research](research/EV_Battery_Health_Monitor_Industry_Standards.md)** - Comprehensive analysis of EV battery monitoring industry practices, tech stack validation, and market research
- **[WSL2 Development Guide](docs/wsl-guide.md)** - Complete setup guide for Windows development using WSL2
- **[Docker Setup Guide](docs/docker-guide.md)** - Detailed PostgreSQL/TimescaleDB database setup, troubleshooting, and testing
- **[Project Plan](ev-battery-health-monitor.md)** - Original project conception and technical roadmap

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
