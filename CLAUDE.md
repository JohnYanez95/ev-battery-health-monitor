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
- **develop**: Integration branch created ✅
- **feature/phase-1-data-sim**: Active development branch ✅
- **Current Phase**: Phase 1 - Data Simulation Engine 🚀

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
docker exec ev-battery-postgres psql -U ev_monitor_user -d battery_health -c "SELECT * FROM timescaledb_information.hypertables;"

# Monitor WSL2 memory usage
wsl --list --verbose
```

---

## Notes During Implementation

### Phase 1 Development Notes ✅ COMPLETED

**Branch**: `feature/phase-1-data-sim`
**Status**: Phase 1 Complete - Data simulation engine fully operational!

**✅ ALL TASKS COMPLETED**:

1. **Industry research reading** - All mandatory sections reviewed
2. **TimescaleDB schema created** - Comprehensive time-series schema with:
   - Main `battery_telemetry` hypertable (1-week partitions, compression enabled)
   - `anomaly_events` table for interactive labeling feature
   - `vehicles` and `charging_sessions` tables
   - Continuous aggregates for performance (`telemetry_hourly`)
   - Sample vehicles inserted (Tesla Model 3, Nissan Leaf)
3. **Database connection module** - Connection pooling with psycopg2
4. **Battery physics simulation engine** - Realistic battery model with:
   - Lithium-ion voltage curves based on SoC
   - Temperature effects and thermal modeling
   - Internal resistance and voltage drops under load
   - State of Health (SoH) tracking
5. **Driving patterns implemented** - Multiple realistic modes:
   - City driving with stop-and-go traffic
   - Highway cruising with passing maneuvers
   - Aggressive driving patterns
   - Eco-friendly efficient driving
   - Mixed daily patterns
6. **CC-CV charging profiles** - Industry-standard charging:
   - AC Level 1 (1.4 kW) home outlet
   - AC Level 2 (11 kW) home/public chargers
   - DC Fast Charging (50 kW) CHAdeMO/CCS
   - Supercharger (150 kW) with thermal management
   - Smart charging with electricity price optimization
7. **Anomaly generation system** - Realistic fault scenarios:
   - Thermal events (cooling system failures)
   - Sensor glitches (spikes, dropouts, noise)
   - Capacity fade simulation
   - Charging anomalies (slow charge, interruptions)
   - Rapid degradation events
8. **Data ingestion tested** - Successfully processed:
   - 86,400 telemetry records/day (1 Hz sampling)
   - Batch insertion with error handling
   - Verified data integrity in TimescaleDB
   - Continuous aggregates working

**📊 Simulation Performance**:
- **Data Volume**: 86,400 records/day per vehicle
- **Realistic Patterns**: Battery discharged 80% → 6.9% in daily use
- **Temperature Range**: 23.9°C - 38.4°C (realistic thermal behavior)
- **Energy Usage**: 169.5 Ah daily consumption
- **Database Performance**: Batch inserts completed in seconds

**🔧 Technical Implementation**:
- **Modular Design**: Separate modules for battery, driving, charging, anomalies, user profiles
- **Physics-Based**: Voltage curves, thermal dynamics, I²R losses
- **Industry Standards**: Tesla 500ms intervals, standard units (V, A, °C, %)
- **User Behavior Profiles**: 8 distinct personalities affecting driving and charging patterns
- **Extensible**: Easy to add new vehicle types, anomaly patterns, or user profiles

**🧑 User Profile System** (New Enhancement):
- **Profile Types**: Night Owl, Early Bird, Spontaneous, Cautious, Commuter, Weekend Warrior, Eco-Conscious, Performance Enthusiast
- **Behavioral Factors**: Wake/sleep times, driving preferences, charging habits, spontaneity levels
- **Smart Charging Logic**: Profiles determine when and how users charge (anxiety levels, target SoC)
- **Driving Patterns**: Each profile has unique distance patterns, speed preferences, and trip timing
- **Prevents Unrealistic Scenarios**: Cautious users never let SoC drop below 50%, Night Owls often forget to charge

**Next Phase**: Phase 1.5 - Simulator Calibration & Research Integration

### Phase 1.5 Development Notes 🚧 CURRENT PRIORITY

**Branch**: `feature/phase-1-data-sim`
**Status**: Significant progress on V2 calibration with research-based user profiles

**✅ MAJOR IMPROVEMENTS COMPLETED**:

1. **Research Integration Complete**: 
   - ✅ Analyzed comprehensive "Charging Behavior of American EV Drivers" research
   - ✅ Identified specific data points for calibration
   - ✅ Created realistic target metrics based on industry studies

2. **V2 User Profiles System**: 
   - ✅ Created `user_profiles_v2.py` with research-calibrated behavior
   - ✅ **COMMON_DRIVER** baseline profile representing typical EV driver
   - ✅ SoC management: 25-85% range (common case from research)
   - ✅ Charging frequency: 4.5 times/week (realistic average)
   - ✅ Daily distances: 28-40 miles (center of 19-50 mile research range)

3. **Safety & Logic Improvements**:
   - ✅ Safety override prevents dangerous <15% SoC
   - ✅ Force charging after 4 days to prevent stranding
   - ✅ Weekly charging frequency tracking and limits
   - ✅ Realistic daily distance caps (150km weekend, 120km weekday)

4. **Development Environment**:
   - ✅ Created `notebooks/workspace.ipynb` for interactive testing
   - ✅ V2 profiles ready for validation and iteration

**📊 ACHIEVED TARGET METRICS**:
- ✅ **SoC Management**: 25-85% realistic comfort zone
- ✅ **Charging frequency**: 3-7 times per week (4.5 average)
- ✅ **Daily distance**: 19-50 mile range validated
- ✅ **Safety buffers**: Prevent <15% SoC dangerous levels
- ✅ **Enhanced charging logic**: Hours tracking and session counting
- ✅ **Miles conversion**: Complete transition from km to miles
- ✅ **Charging types**: Night, opportunity, emergency classification

**✅ COMPLETED TASKS**:
- [x] **Thermal Safety System** - Multi-level protection (50°C warning, 55°C critical, 60°C shutdown, 45°C recovery)
- [x] **Standardized Testing Framework** - Organized thermal testing with backend/plotting/ module
- [x] **Thermal Validation** - Normal vs extreme condition tests with comprehensive visualization

**🚧 REMAINING TASKS**:
- [ ] Additional user profiles (COMMUTER, WEEKEND_WARRIOR, etc.)
- [ ] Full validation testing in notebook
- [x] Integration with existing simulator pipeline ✅ (Enhanced charging details)

**🔬 Research Integration Status**:
- ✅ Decomposed American EV charging behavior research
- ✅ Incorporated real-world statistics into COMMON_DRIVER profile
- ✅ Validated design against research data points
- [ ] Cross-reference with additional industry studies

### Thermal Safety System Implementation (Aug 2nd, 2025)

**📖 READ SECTION 5: Implementation Guidance - "Battery Safety and Thermal Management"**
**When:** Implementing temperature monitoring and safety shutoffs
**Key Focus:**
- Multi-level thermal protection (warning → critical → shutdown → recovery)
- Power limiting based on temperature to prevent overheating
- Industry-standard temperature thresholds for lithium-ion batteries
- Emergency shutdown protocols and recovery procedures

**✅ IMPLEMENTATION COMPLETED**:
1. **thermal_safety.py** - Complete thermal management system:
   - **Warning**: 50°C (70% power limit, logging)
   - **Critical**: 55°C (30% power limit, urgent alerts)
   - **Shutdown**: 60°C (0% power, emergency stop)
   - **Recovery**: 45°C (resume normal operation)
   - Event logging and thermal history tracking

2. **Battery Model Integration**:
   - Integrated ThermalSafetyManager into BatteryModel
   - Real-time temperature monitoring in update_thermal()
   - Power limiting in apply_current() method
   - Thermal status included in battery state output

3. **Standardized Testing Framework**:
   - **backend/plotting/battery_plots.py** - Reusable plotting functions
   - **test_thermal_safety_good.py** - Normal operation validation
   - **test_thermal_safety_extreme.py** - Extreme conditions testing
   - **test_thermal_comparison.py** - Side-by-side analysis
   - Identical test structure (600s, 3 phases) for apples-to-apples comparison

4. **Validation Results**:
   - **Normal Operation**: Max 25.7°C, no thermal events, no power limiting
   - **Extreme Conditions**: Max 60.0°C, all safety levels triggered, power limited to 30-0%
   - Comprehensive visualization with 4-subplot standardized format

**File Structure**:
```
backend/
├── simulation/
│   ├── thermal_safety.py          # Multi-level thermal protection
│   └── battery_model.py           # Integrated thermal monitoring
├── plotting/
│   ├── __init__.py
│   └── battery_plots.py           # Standardized test visualization
├── test_thermal_safety_good.py    # Normal operation test
├── test_thermal_safety_extreme.py # Extreme conditions test
└── test_thermal_comparison.py     # Comparison analysis
figures/
├── test_thermal_safety_good.png   # Normal operation results
└── test_thermal_safety_extreme.png # Extreme conditions results
```

### Current Priority: Thermal Research Validation (Aug 2nd, 2025)

**🚧 RESEARCH IN PROGRESS**: Validating thermal model authenticity before proceeding with simulation refinements

**Research Question**: Are our 82-second thermal progressions (31s warning → 47s critical → 113s shutdown) realistic for EV battery thermal events?

**ChatGPT Query Status**: 
- ✅ Comprehensive thermal research query submitted (NCM chemistry focus)
- ✅ Simulation context provided (Tesla Model 3 parameters, extreme conditions)
- 🚧 Awaiting detailed thermal modeling research findings
- ⏳ Will apply research to calibrate battery thermal parameters

**Development Pause Rationale**: 
- Thermal authenticity is critical for automotive industry credibility
- Better to validate model accuracy before building additional features
- Research-driven approach demonstrates systematic engineering methodology

**Next Actions**:
1. Review ChatGPT thermal research findings
2. Calibrate thermal model parameters (heat generation, cooling rates, timescales)
3. Re-run thermal safety tests with improved realism
4. Resume Phase 1.5 development with validated thermal model

**Next Phase**: Complete Phase 1.5 with research-validated thermal model, then Phase 2 - Backend API Development (FastAPI)
