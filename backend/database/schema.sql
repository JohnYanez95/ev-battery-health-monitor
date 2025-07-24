-- EV Battery Health Monitor - TimescaleDB Schema
-- Based on industry standards research: Tesla 500ms intervals, standard metrics, wide table approach

-- Create database extension if not exists
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Main telemetry table using wide table approach for performance
-- Primary key: (vehicle_id, time) as recommended in research
CREATE TABLE IF NOT EXISTS battery_telemetry (
    time TIMESTAMPTZ NOT NULL,
    vehicle_id TEXT NOT NULL,
    
    -- Core battery metrics (Section 1: Key Metrics Tracked)
    soc_percent REAL CHECK (soc_percent >= 0 AND soc_percent <= 100),  -- State of Charge (%)
    voltage REAL CHECK (voltage >= 0 AND voltage <= 1000),              -- Pack voltage (V) - typical range 300-420V
    current REAL CHECK (current >= -500 AND current <= 500),            -- Current (A) - negative when discharging
    temperature REAL CHECK (temperature >= -50 AND temperature <= 100),  -- Battery temp (°C)
    
    -- Derived metrics
    power REAL GENERATED ALWAYS AS (voltage * current) STORED,          -- Power (W) = V * A
    energy_kwh REAL,                                                     -- Energy remaining (kWh)
    
    -- Additional monitoring metrics
    soh_percent REAL CHECK (soh_percent >= 0 AND soh_percent <= 100),   -- State of Health (%)
    max_cell_temp REAL,                                                  -- Max cell temperature (°C)
    min_cell_temp REAL,                                                  -- Min cell temperature (°C)
    ambient_temp REAL,                                                   -- Outside temperature (°C)
    
    -- Vehicle state and context
    is_charging BOOLEAN DEFAULT FALSE,                                   -- Charging state flag
    is_driving BOOLEAN DEFAULT FALSE,                                    -- Driving state flag
    speed_kmh REAL DEFAULT 0,                                           -- Vehicle speed (km/h)
    location_lat REAL,                                                  -- GPS latitude
    location_lon REAL,                                                  -- GPS longitude
    
    -- Range estimation
    estimated_range_km REAL,                                            -- Estimated remaining range (km)
    
    -- Metadata
    data_quality INTEGER DEFAULT 100,                                   -- Data quality score (0-100)
    
    PRIMARY KEY (vehicle_id, time)
);

-- Convert to TimescaleDB hypertable with 1-week chunks
-- This follows best practices from Section 3: Architecture
SELECT create_hypertable(
    'battery_telemetry',
    'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_time 
    ON battery_telemetry (vehicle_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_soc 
    ON battery_telemetry (soc_percent, time DESC) 
    WHERE soc_percent < 20;  -- Low battery alerts

CREATE INDEX IF NOT EXISTS idx_telemetry_temperature 
    ON battery_telemetry (temperature, time DESC) 
    WHERE temperature > 45;  -- High temperature alerts

-- Table for labeled anomaly events (core feature)
CREATE TABLE IF NOT EXISTS anomaly_events (
    event_id SERIAL PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    
    -- User labeling metadata
    labeled_by TEXT,
    labeled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- ML training flags
    verified BOOLEAN DEFAULT FALSE,
    used_for_training BOOLEAN DEFAULT FALSE,
    
    -- Ensure end time is after start time
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

-- Index for efficient anomaly queries
CREATE INDEX IF NOT EXISTS idx_anomaly_vehicle_time 
    ON anomaly_events (vehicle_id, start_time, end_time);

CREATE INDEX IF NOT EXISTS idx_anomaly_type 
    ON anomaly_events (event_type);

-- Table for vehicle metadata
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    make TEXT,
    model TEXT,
    year INTEGER,
    battery_capacity_kwh REAL,
    
    -- Battery specifications
    nominal_voltage REAL,
    cell_configuration TEXT,  -- e.g., "96s74p" for Tesla Model S
    chemistry_type TEXT,      -- e.g., "NCA", "LFP", "NMC"
    
    -- Fleet management
    fleet_id TEXT,
    in_service_date DATE,
    odometer_km REAL,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Table for charging sessions (derived from telemetry)
CREATE TABLE IF NOT EXISTS charging_sessions (
    session_id SERIAL PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    
    -- Charging metrics
    start_soc REAL,
    end_soc REAL,
    energy_delivered_kwh REAL,
    max_charging_power_kw REAL,
    charging_type TEXT CHECK (charging_type IN ('AC_L1', 'AC_L2', 'DC_FAST', 'SUPERCHARGER')),
    
    -- Location
    station_id TEXT,
    location_lat REAL,
    location_lon REAL,
    
    -- Session status
    completed BOOLEAN DEFAULT FALSE,
    interrupted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

-- Create continuous aggregate for hourly statistics (performance optimization)
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    vehicle_id,
    
    -- Aggregated metrics
    AVG(soc_percent) AS avg_soc,
    MIN(soc_percent) AS min_soc,
    MAX(soc_percent) AS max_soc,
    
    AVG(voltage) AS avg_voltage,
    AVG(current) AS avg_current,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    
    AVG(power) AS avg_power,
    SUM(CASE WHEN power > 0 THEN power * 1/3600.0 ELSE 0 END) AS energy_charged_kwh,
    SUM(CASE WHEN power < 0 THEN ABS(power) * 1/3600.0 ELSE 0 END) AS energy_discharged_kwh,
    
    -- State counters
    SUM(CASE WHEN is_charging THEN 1 ELSE 0 END) AS charging_count,
    SUM(CASE WHEN is_driving THEN 1 ELSE 0 END) AS driving_count,
    
    COUNT(*) AS sample_count
FROM battery_telemetry
GROUP BY hour, vehicle_id
WITH NO DATA;

-- Create refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Create view for latest vehicle status (fleet dashboard)
CREATE OR REPLACE VIEW vehicle_current_status AS
WITH latest_telemetry AS (
    SELECT DISTINCT ON (vehicle_id)
        vehicle_id,
        time,
        soc_percent,
        voltage,
        current,
        temperature,
        soh_percent,
        is_charging,
        is_driving,
        estimated_range_km,
        location_lat,
        location_lon
    FROM battery_telemetry
    WHERE time > NOW() - INTERVAL '1 hour'
    ORDER BY vehicle_id, time DESC
)
SELECT 
    v.vehicle_id,
    v.make,
    v.model,
    lt.time AS last_update,
    lt.soc_percent,
    lt.temperature,
    lt.soh_percent,
    lt.is_charging,
    lt.is_driving,
    lt.estimated_range_km,
    lt.location_lat,
    lt.location_lon,
    CASE 
        WHEN lt.time < NOW() - INTERVAL '10 minutes' THEN 'offline'
        WHEN lt.is_charging THEN 'charging'
        WHEN lt.is_driving THEN 'driving'
        ELSE 'idle'
    END AS status
FROM vehicles v
LEFT JOIN latest_telemetry lt ON v.vehicle_id = lt.vehicle_id;

-- Function to calculate SoH based on charge cycles (simplified version)
CREATE OR REPLACE FUNCTION calculate_soh(
    p_vehicle_id TEXT,
    p_reference_date TIMESTAMPTZ DEFAULT NOW()
) RETURNS REAL AS $$
DECLARE
    initial_capacity REAL;
    current_capacity REAL;
    soh REAL;
BEGIN
    -- Get vehicle's battery capacity
    SELECT battery_capacity_kwh INTO initial_capacity
    FROM vehicles
    WHERE vehicle_id = p_vehicle_id;
    
    -- Calculate current capacity based on recent full charge
    -- This is simplified - real SoH calculation is more complex
    WITH recent_full_charge AS (
        SELECT 
            MAX(energy_kwh) AS max_energy
        FROM battery_telemetry
        WHERE vehicle_id = p_vehicle_id
          AND soc_percent > 95
          AND time > p_reference_date - INTERVAL '30 days'
          AND time <= p_reference_date
    )
    SELECT max_energy INTO current_capacity
    FROM recent_full_charge;
    
    -- Calculate SoH as percentage
    IF initial_capacity > 0 AND current_capacity IS NOT NULL THEN
        soh := (current_capacity / initial_capacity) * 100;
        -- Industry standard: cap at 100% and floor at 0%
        soh := GREATEST(0, LEAST(100, soh));
    ELSE
        soh := NULL;
    END IF;
    
    RETURN soh;
END;
$$ LANGUAGE plpgsql;

-- Enable compression on the hypertable first
ALTER TABLE battery_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'vehicle_id'
);

-- Compression policy for older data (reduce storage by 90%+ as per TimescaleDB benchmarks)
SELECT add_compression_policy('battery_telemetry', 
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Data retention policy (keep raw data for 3 months, use continuous aggregates for older)
-- Commented out by default - enable based on requirements
-- SELECT add_retention_policy('battery_telemetry', 
--     INTERVAL '3 months',
--     if_not_exists => TRUE
-- );

-- Grant permissions (adjust based on your user setup)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ev_monitor_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ev_monitor_user;