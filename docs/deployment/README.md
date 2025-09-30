# Deployment Documentation

This directory contains deployment guides and configuration documentation.

## Available Guides

- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment (coming soon)
- **[Docker Guide](DOCKER.md)** - Docker containerization (coming soon)
- **[Configuration Guide](CONFIGURATION.md)** - Configuration options (coming soon)

## Current Deployment

The project currently uses:
- Docker support (see [Dockerfile](../../Dockerfile))
- Docker Compose (see [docker-compose.yml](../../docker-compose.yml))

## Quick Start with Docker

```bash
# Build the image
docker build -t odcs-converter .

# Run with Docker Compose
docker-compose up
```

---

**Status**: Documentation in progress
**Last Updated**: 2025-01-26
