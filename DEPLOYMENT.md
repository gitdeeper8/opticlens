# 🚀 OPTICLENS Deployment Guide

## Deployment Options

### 1. Local Deployment

```bash
# Start API server
opticlens serve --api --port 8000

# Start dashboard
opticlens dashboard --port 8501

# In another terminal, run simulation
opticlens simulate --mie --wavelengths 0.44,0.55,0.67
```

2. Docker Deployment

```bash
# Using docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale api=3
```

3. Cloud Deployment (AWS)

```bash
# Using AWS CLI
aws ecs create-cluster --cluster-name opticlens-prod

# Deploy with ECS
ecs-cli compose --file docker-compose.yml \
  --project-name opticlens \
  service up
```

4. Netlify Dashboard

```bash
# Deploy dashboard to Netlify
cd dashboard
npm run build
netlify deploy --prod --dir=build
```

Mission Planning

Pre-Deployment Checklist

```python
from opticlens.deployment import MissionPlanner

planner = MissionPlanner(
    station="GSFC",
    wavelength=0.55,
    duration_hours=24
)

# Check atmospheric conditions
conditions = planner.check_conditions()
# Returns: {'aod': 0.12, 'turbulence': 'moderate', 'clouds': False}

# Validate instrument configuration
config_valid = planner.validate_instruments(
    instruments=['sun_photometer', 'lidar'],
    sampling_rate=0.1  # Hz
)

# Generate deployment script
planner.generate_script(
    output="deploy_mission.sh"
)
```

Real-Time Monitoring

```python
from opticlens.deployment import MissionMonitor

monitor = MissionMonitor(
    mission_id="gsfc_2026_001"
)

# Monitor instrument status
status = monitor.instrument_status()
# Returns: {'active': 3, 'aod_accuracy': 0.01, 'battery': 92}

# Check alerts
alerts = monitor.active_alerts()
# Returns: [{'level': 'WATCH', 'message': 'Turbulence increasing'}]

# Visualize in real-time
monitor.launch_dashboard(port=8501)
```

Data Management

Data Ingestion

```python
from opticlens.deployment import DataManager

manager = DataManager(
    data_dir="/data/opticlens",
    backup_dir="/backups/opticlens"
)

# Ingest real-time data
manager.ingest_realtime(
    sources=['aeronet', 'modis', 'calipso'],
    interval=3600  # seconds
)

# Archive mission data
manager.archive_mission(
    mission_id="gsfc_2026_001",
    compress=True
)

# Query historical data
historical = manager.query(
    station="GSFC",
    parameters=['aod', 'angstrom', 'water_vapor'],
    time_range=["2026-01-01", "2026-03-01"]
)
```

Backup and Recovery

Automated Backup Script

```bash
cat > backup.sh << 'EOF'
#!/bin/bash
# backup.sh - OPTICLENS Backup Script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/opticlens"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup (TimescaleDB)
pg_dump -h localhost -U opticlens_user opticlens | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# AERONET data backup
tar -czf $BACKUP_DIR/aeronet_$DATE.tar.gz /data/aeronet

# MODIS data backup
tar -czf $BACKUP_DIR/modis_$DATE.tar.gz /data/modis

# CALIPSO data backup
tar -czf $BACKUP_DIR/calipso_$DATE.tar.gz /data/calipso

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/opticlens

# Results backup
tar -czf $BACKUP_DIR/results_$DATE.tar.gz /data/results

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
