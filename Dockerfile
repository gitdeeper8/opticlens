FROM python:3.10-slim

LABEL maintainer="gitdeeper@gmail.com"
LABEL version="1.0.0"
LABEL description="OPTICLENS - Optical Phenomena, Turbulence & Imaging --- Light Environmental Nonlinearity System"

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
