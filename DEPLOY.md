# 🔭 OPTICLENS DEPLOYMENT GUIDE

This guide covers deployment options for the OPTICLENS framework, including the live dashboard, API services, documentation, and real-time data pipelines.

---

## Quick Deployments

### Netlify (Dashboard)

The OPTICLENS interactive dashboard is pre-configured for Netlify deployment at [opticlens.netlify.app](https://opticlens.netlify.app).

#### Automatic Deployment

1. Connect your Git repository to Netlify
2. Use these settings:
   - Build command: `mkdocs build`
   - Publish directory: `site`
   - Environment variables: none required

3. Or use the `netlify.toml` configuration:

```toml
[build]
  command = "mkdocs build"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.11"
  MKDOCS_CONFIG = "mkdocs.yml"

[[redirects]]
  from = "/api/*"
  to = "https://opticlens.netlify.app/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Access-Control-Allow-Origin = "https://opticlens.netlify.app"
```

Manual Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=site
```

Live dashboard: https://opticlens.netlify.app
API endpoint: https://opticlens.netlify.app/api

---

ReadTheDocs (Documentation)

Deploy technical documentation to ReadTheDocs.

Configuration

1. Connect your Git repository to readthedocs.org
2. Use the .readthedocs.yaml configuration in this repository
3. Build documentation automatically on push

Documentation: https://opticlens.readthedocs.io

---

PyPI (Python Package)

Deploy the core OPTICLENS package to PyPI.

Preparation

```bash
# Install build tools
pip install build twine

# Update version in setup.py/pyproject.toml
# Version: 1.0.0

# Create distribution files
python -m build
```

Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Install
pip install opticlens
```

PyPI package: https://pypi.org/project/opticlens

---

Docker Deployment

Build Image

```dockerfile
# Dockerfile
FROM python:3.10-slim

LABEL maintainer="gitdeeper@gmail.com"
LABEL version="1.0.0"
LABEL description="OPTICLENS - Optical Phenomena, Turbulence & Imaging"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OPTICLENS_HOME=/opt/opticlens \
    OPTICLENS_CONFIG=/etc/opticlens/config.yaml \
    TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 -s /bin/bash opticlens && \
    mkdir -p /opt/opticlens && \
    mkdir -p /etc/opticlens && \
    mkdir -p /data/aeronet && \
    mkdir -p /data/modis && \
    mkdir -p /data/calipso && \
    mkdir -p /data/results && \
    chown -R opticlens:opticlens /opt/opticlens /etc/opticlens /data

USER opticlens
WORKDIR /opt/opticlens

COPY --chown=opticlens:opticlens requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=opticlens:opticlens . .

RUN pip install --user -e .

EXPOSE 8000 8501 9090

CMD ["opticlens", "serve", "--all"]
```

Build and Run

```bash
# Build image
docker build -t opticlens:1.0.0 .

# Run container
docker run -d \
  --name opticlens-prod \
  -p 8000:8000 \
  -p 8501:8501 \
  -p 9090:9090 \
  -v /host/data:/data \
  -v /host/config:/etc/opticlens \
  -e OPTICLENS_CONFIG=/etc/opticlens/config.yaml \
  -e NASA_EARTHDATA_TOKEN=your_token_here \
  -e AERONET_API_KEY=your_key_here \
  --restart unless-stopped \
  opticlens:1.0.0
```

Docker Compose

Use the provided docker-compose.yml for full-stack deployment:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

Configuration

Production Configuration

```yaml
# config/opticlens.prod.yaml
# OPTICLENS Production Configuration

version: 1.0
environment: production

server:
  host: 0.0.0.0
  api_port: 8000
  dashboard_port: 8501
  metrics_port: 9090
  workers: 4
  timeout: 120

database:
  host: postgres
  port: 5432
  name: opticlens
  user: opticlens_user
  password: ${DB_PASSWORD}
  pool_size: 20
  hypertable_chunk: 7  # days

redis:
  host: redis
  port: 6379
  db: 0
  maxmemory: 512mb

monitoring:
  aeroenet_update_interval: 3600  # seconds (hourly)
  modis_update_interval: 86400    # seconds (daily)
  calipso_update_interval: 86400  # seconds (daily)
  forecast_horizon: 24  # hours
  ensemble_members: 10
  metrics_enabled: true

security:
  jwt_secret: ${JWT_SECRET}
  jwt_expiry_hours: 24
  rate_limit: 100/minute
  cors_origins:
    - https://opticlens.netlify.app
    - https://opticlens.readthedocs.io

api:
  public_url: https://opticlens.netlify.app/api
  docs_url: https://opticlens.readthedocs.io/api
  version: v1

external_apis:
  nasa_earthdata:
    url: https://earthdata.nasa.gov/
    token: ${NASA_EARTHDATA_TOKEN}
    
  aeronet:
    url: https://aeronet.gsfc.nasa.gov/
    api_key: ${AERONET_API_KEY}
    endpoints:
      direct_sun: /cgi-bin/print_web_data_v3
      inversion: /cgi-bin/print_web_data_inv_v3
    
  modis:
    url: https://modis.gsfc.nasa.gov/
    api_key: ${MODIS_API_KEY}
    products:
      - MOD04_L2  # aerosol
      - MOD021KM  # radiance
    
  calipso:
    url: https://www-calipso.larc.nasa.gov/
    api_key: ${CALIPSO_API_KEY}
    products:
      - level2_aerosol_profile
      - level2_cloud_layer

data:
  aeronet_dir: /data/aeronet
  modis_dir: /data/modis
  calipso_dir: /data/calipso
  results_dir: /data/results
  max_file_size: 10GB
  retention_days:
    raw: 90
    hourly: 365
    daily: 730
    monthly: permanent

stations:
  monitored:
    - name: "GSFC"
      lat: 38.992
      lon: -76.840
      altitude: 87
    - name: "Lille"
      lat: 50.611
      lon: 3.141
      altitude: 60
    - name: "Barcelona"
      lat: 41.386
      lon: 2.117
      altitude: 125
    - name: "Osaka"
      lat: 34.651
      lon: 135.591
      altitude: 50
    - name: "Canberra"
      lat: -35.282
      lon: 149.128
      altitude: 577

alerts:
  levels:
    critical: 39
    warning: 59
    watch: 79
    caution: 94
  notification_endpoints:
    email: alerts@opticlens.space
    webhook: https://hooks.slack.com/services/...
```

---

Real-Time Data Pipeline

Data Sources Configuration

```yaml
# config/data_sources.yaml
sources:
  aeronet:
    type: rest_api
    url: https://aeronet.gsfc.nasa.gov/
    interval: 3600  # hourly
    format: csv
    parameters:
      - AOD_340nm
      - AOD_380nm
      - AOD_440nm
      - AOD_500nm
      - AOD_675nm
      - AOD_870nm
      - AOD_1020nm
      - Angstrom_440_870
      - Precipitable_Water
      - Single_Scattering_Albedo
      
  modis:
    type: rest_api
    url: https://modis.gsfc.nasa.gov/api/
    interval: 86400  # daily
    format: hdf
    products:
      - MOD04_L2:  # Aerosol product
          variables:
            - Optical_Depth_Land
            - Optical_Depth_Ocean
            - Angstrom_Exponent_Land
            - Fine_Mode_Fraction
            
  calipso:
    type: rest_api
    url: https://www-calipso.larc.nasa.gov/api/
    interval: 86400  # daily
    format: hdf
    products:
      - level2_aerosol:
          variables:
            - Extinction_Profile
            - Backscatter_Profile
            - Depolarization_Ratio
            - Aerosol_Type
```

Data Ingestion Service

```bash
# Start data ingestion service
opticlens ingest --config config/data_sources.yaml --daemon

# Monitor ingestion status
opticlens status --sources all

# Force update for specific station
opticlens update --station GSFC --force
```

---

Monitoring

Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'opticlens-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    scrape_interval: 10s
    
  - job_name: 'opticlens-dashboard'
    static_configs:
      - targets: ['dashboard:8501']
    metrics_path: /metrics
    
  - job_name: 'opticlens-processor'
    static_configs:
      - targets: ['processor:9090']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
```

Grafana Dashboard

Import the OPTICLENS dashboard template to visualize:

· Real-time aerosol optical depth with 1-hour resolution
· Ångström exponent and fine mode fraction
· Turbulence parameters (Cn2, scintillation index, Fried parameter)
· Refractive index profiles
· Mie scattering phase functions
· Halo simulations and mirage displacements
· AERONET station comparisons
· MODIS and CALIPSO overpass data
· 5-tier alert system
· System health metrics
· Data ingestion latency

Alerting Rules

```yaml
# alerts/opticlens.rules.yml
groups:
  - name: opticlens_critical
    rules:
      - alert: AODCritical
        expr: aerosol_optical_depth > 1.0
        for: 30m
        annotations:
          summary: "Aerosol Optical Depth in CRITICAL range (>1.0)"
          description: "Heavy aerosol loading detected"
          
      - alert: TurbulenceHigh
        expr: cn2 > 1e-13
        for: 15m
        annotations:
          summary: "Extreme turbulence (Cn2 > 1e-13)"
          
      - alert: ScintillationSevere
        expr: scintillation_index > 0.3
        for: 10m
        annotations:
          summary: "Strong scintillation detected"
          
      - alert: DataStale
        expr: time() - last_aeronet_ingest > 7200
        for: 5m
        annotations:
          summary: "AERONET data stale (>2 hours old)"
```

---

Quick Reference

```bash
# Netlify Dashboard
https://opticlens.netlify.app
https://opticlens.netlify.app/api

# PyPI Package
pip install opticlens

# Docker
docker pull gitlab.com/gitdeeper8/opticlens:latest

# Documentation
https://opticlens.readthedocs.io

# Source Code
https://gitlab.com/gitdeeper8/opticlens
https://github.com/gitdeeper8/opticlens

# Data Sources
https://aeronet.gsfc.nasa.gov
https://modis.gsfc.nasa.gov
https://www-calipso.larc.nasa.gov
```

---

Support

For deployment assistance:

· Dashboard: https://opticlens.netlify.app
· Documentation: https://opticlens.readthedocs.io
· Issues: https://gitlab.com/gitdeeper8/opticlens/-/issues
· Email: deploy@opticlens.space
· Principal Investigator: gitdeeper@gmail.com

---

🔭 Light does not simply travel through the atmosphere — it is shaped, scattered, bent, and dispersed by it.

DOI: 10.5281/zenodo.OPTICLENS.2026
