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

### 🔋 Simulation Capabilities (Phase 1 Complete!)

- **Realistic Battery Physics** - Lithium-ion voltage curves, thermal dynamics, I²R losses
- **Multiple Driving Patterns** - City, highway, aggressive, eco-friendly, mixed modes
- **Industry-Standard Charging** - CC-CV profiles for L1/L2/DC Fast/Supercharger
- **Anomaly Scenarios** - Thermal events, sensor glitches, capacity fade, charging issues
- **High-Frequency Data** - 1Hz sampling rate (86,400 points/day per vehicle)
- **Multiple Vehicles** - Tesla Model 3 and Nissan Leaf profiles included
- **User Behavior Profiles** - 8 personality types (Cautious, Spontaneous, Night Owl, etc.)

⚠️ **Known Issues with V2 Simulator** (To be addressed in Phase 1.5):
- Charging behavior calibration needs refinement (currently over-charging)
- User profile driving patterns need realistic daily distance limits
- Temperature modeling requires safety limits and thermal management
- Energy consumption rates need validation against real-world data

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

### Running the Simulation

```bash
# Generate realistic EV battery data
python backend/simulation/simulator.py

# Run simulation with specific user profile
python -c "
from backend.simulation.simulator import run_simulation
from backend.simulation.user_profiles import UserProfile
run_simulation('VEH001', days=7, user_profile=UserProfile.CAUTIOUS)
"

# Test different user behaviors
python backend/test_user_profiles.py

# Test the simulation pipeline
python backend/test_simulation.py
```

### Development

```bash
# Start the development servers (coming in Phase 2)
# npm run dev          # Frontend (port 3000)
# python -m uvicorn main:app --reload  # Backend (port 8000)
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

### 🧑 User Behavior Profiles

The simulation includes 8 distinct user personalities that affect driving and charging patterns:

- **🦉 Night Owl** - Late sleeper, forgets to charge, spontaneous trips
- **🌅 Early Bird** - Early riser, always charges at night, planned trips
- **🎲 Spontaneous** - Unpredictable schedule, lets battery get low, random charging
- **🛡️ Cautious** - Never lets SoC drop below 50%, charges frequently, eco driving
- **🚗 Commuter** - Regular work schedule, consistent patterns, weekend rest
- **🏔️ Weekend Warrior** - Minimal weekday use, long weekend trips
- **🌱 Eco-Conscious** - Optimizes for efficiency, off-peak charging, gentle driving
- **🏁 Performance Enthusiast** - Aggressive driving, high energy use, frequent charging

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
- [x] **Phase 1: Data simulation engine** ✅ *Completed!*
  - [x] TimescaleDB schema with hypertables and compression
  - [x] Database connection pooling module
  - [x] Battery physics simulation engine
  - [x] Charging/discharging patterns (CC-CV)
  - [x] Anomaly generation system
  - [x] Data ingestion tested (86,400 records/day @ 1Hz)
- [ ] **Phase 2: Backend API development** ← *Next up*
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
