# Claude Code Implementation Notes

## Industry Research Reference Points

This document tracks when to reference specific sections of our [Industry Standards Research](research/EV_Battery_Health_Monitor_Industry_Standards.md) during implementation.

---

## Git Branch Strategy

### Branch Naming Convention
```
main                    # Production-ready code, stable releases
develop                 # Integration branch for features
feature/phase-1-data-sim # Individual feature branches
feature/phase-2-ui      # Individual feature branches
feature/phase-3-labeling # Individual feature branches
hotfix/critical-bug     # Emergency fixes
docs/update-readme      # Documentation updates
```

### Development Workflow
1. **Create feature branch** from `develop`
2. **Implement and test** feature locally
3. **Create PR** to merge into `develop`
4. **Test integration** on `develop` branch
5. **Merge to main** when phase is complete and stable

### Phase-Based Branch Plan

#### Phase 1: Data Simulation Engine
```bash
git checkout develop
git checkout -b feature/phase-1-data-sim
# Implement: simulation engine, realistic EV patterns, anomaly generation
# PR: feature/phase-1-data-sim → develop
```

#### Phase 2: Database & Backend Setup
```bash
git checkout develop
git checkout -b feature/phase-2-backend
# Implement: TimescaleDB setup, FastAPI, data ingestion endpoints
# PR: feature/phase-2-backend → develop
```

#### Phase 3: Frontend & Visualization
```bash
git checkout develop
git checkout -b feature/phase-3-frontend
# Implement: React/Next.js UI, Plotly charts, basic visualization
# PR: feature/phase-3-frontend → develop
```

#### Phase 4: Interactive Labeling (Standout Feature)
```bash
git checkout develop
git checkout -b feature/phase-4-labeling
# Implement: click-and-drag labeling, event categorization, data persistence
# PR: feature/phase-4-labeling → develop
```

#### Phase 5: Export & Polish
```bash
git checkout develop
git checkout -b feature/phase-5-export
# Implement: data export, Docker deployment, final polish
# PR: feature/phase-5-export → develop → main
```

### Branch Protection Strategy
- **main**: Require PR reviews, passing tests
- **develop**: Allow direct pushes for rapid iteration
- **feature branches**: Squash merge to keep history clean

### Current Status
- **main**: Documentation and project setup ✅
- **Next**: Create `develop` branch and start Phase 1

---

## Phase 1: Data Simulation Engine

### 📖 **READ SECTION 5: Implementation Guidance - "Realistic Data Simulation"**
**When:** Before writing data generation logic
**Key Focus:**
- EV battery discharge patterns during driving (SoC decreases, current fluctuations, voltage drops under load)
- Charging cycles (CC-CV profile: high current → tapered current as SoC approaches 100%)
- Idle periods (flat SoC, ~0 current, voltage settling)
- Realistic voltage ranges (300-420V) and current ranges (-200A to +200A)

### 📖 **READ SECTION 1: Industry Standards - "Key Metrics Tracked"**
**When:** Defining data schema and units
**Key Focus:**
- Standard units (°C for temp, V for voltage, A for current, % for SoC)
- State of Health (SoH) calculation as ratio of current/original capacity
- Sampling rates (Tesla uses 500ms intervals = 2 Hz)

### 📖 **READ SECTION 5: "Anomalies to Include"**
**When:** Implementing anomaly simulation
**Key Focus:**
- Thermal events (cooling system failure, temp rising > Y°C/min)
- Capacity fade (gradual SoH decline from 100% → 95% over months)
- Sensor glitches (unrealistic voltage/current jumps)
- Charging anomalies (slow charging, interrupted charging)

---

## Phase 2: Database Setup & Schema Design

### 📖 **READ SECTION 3: Architecture Best Practices - "Data Modeling & Partitioning"**
**When:** Setting up TimescaleDB hypertables
**Key Focus:**
- Partition by time (1-week chunks recommended)
- Wide table approach for known metrics vs normalized key-value
- Primary key design: `(vehicle_id, ts)`
- Indexing strategy for time-series queries

### 📖 **READ SECTION 3: "Continuous Aggregations & Downsampling"**
**When:** Implementing data retention policies
**Key Focus:**
- Pre-compute daily/hourly summaries for dashboard performance
- Retention strategy (raw data 3 months → 1-minute averages 1 year → daily stats long-term)
- TimescaleDB compression for older data chunks

### 📖 **READ SECTION 5: "WSL2 + Docker Workflow Best Practices"**
**When:** Configuring PostgreSQL container
**Key Focus:**
- Keep database files in WSL2 filesystem (not Windows mounts)
- Docker volume configuration for performance
- Memory limits via `.wslconfig` if needed

---

## Phase 3: Backend API Development

### 📖 **READ SECTION 1: "Industry Protocols and APIs"**
**When:** Designing API endpoints
**Key Focus:**
- Time-series data structure: `[timestamp, vehicle_id, metric_name, value]`
- REST vs WebSocket patterns (REST for historical, WebSocket for real-time)
- Pagination/aggregation for large time ranges

### 📖 **READ SECTION 3: "Real-Time vs Batch in UI"**
**When:** Planning data serving architecture
**Key Focus:**
- Separate concerns: streaming service vs REST queries
- Optimize historical queries with pre-aggregated data
- Handle time range queries efficiently

---

## Phase 4: Frontend & Visualization

### 📖 **READ SECTION 5: "Visualization Standards in Automotive Dashboards"**
**When:** Designing the UI components
**Key Focus:**
- Color coding (blue for SoC, red for temperature, green for charging current)
- Multiple y-axes for different metrics on same chart
- Dark theme with bright colored lines (automotive standard)
- Interactive features: zoom, pan, range selectors

### 📖 **READ SECTION 5: "Annotation/Labeling UI"**
**When:** Building the anomaly labeling interface
**Key Focus:**
- Click-and-drag time range selection
- Dialog popup for event categorization
- Visual shading/icons for labeled regions
- This is our standout feature - make it polished!

### 📖 **READ SECTION 1: "Sampling Rates & Data Volume"**
**When:** Implementing data pagination/downsampling
**Key Focus:**
- Handle large datasets (millions of points) in browser
- Implement resolution-based API (`resolution=1s` vs `resolution=1min`)
- Plotly performance considerations for large datasets

---

## Phase 5: Advanced Features & Polish

### 📖 **READ SECTION 5: "Features to Stand Out to Employers"**
**When:** Adding SoH tracking and degradation analysis
**Key Focus:**
- State of Health trend visualization
- Battery capacity estimation from charge cycles
- Fleet dashboard overview (if implementing multiple vehicles)
- Remaining Useful Life (RUL) discussion points

### 📖 **READ SECTION 6: "Future-Proofing and Emerging Trends"**
**When:** Preparing interview talking points
**Key Focus:**
- Edge computing considerations
- Federated learning awareness
- EU Battery Passport compliance
- Scaling to cloud architectures

---

## Interview Preparation

### 📖 **READ SECTION 4: Employment Market Analysis**
**When:** Preparing for job interviews
**Key Focus:**
- Tech stack justification (why PostgreSQL/TimescaleDB over InfluxDB)
- Cross-platform development skills (WSL2 benefits)
- Domain knowledge talking points (battery degradation, thermal management)
- Industry awareness (Tesla's 500ms streaming, BMW CarData APIs)

### 📖 **READ SECTION 2: Tech Stack Validation**
**When:** Explaining architectural decisions
**Key Focus:**
- Performance benchmarks (TimescaleDB 90% compression, query speedups)
- Comparison with alternatives (InfluxDB, Prometheus, cloud solutions)
- Job market relevance and transferable skills

---

## Quick Reference Commands

```bash
# Start development environment
docker-compose up -d

# Check TimescaleDB performance
docker exec -it postgres psql -U postgres -c "SELECT * FROM timescaledb_information.hypertables;"

# Monitor WSL2 memory usage
wsl --list --verbose
```

---

## Notes During Implementation

*Use this space to track insights and decisions as we build...*
