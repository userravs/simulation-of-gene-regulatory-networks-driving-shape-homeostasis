# Docker Documentation

## Overview

This project includes Docker support for easy deployment and reproducible environments. Docker ensures that the simulation runs consistently across different systems and eliminates dependency issues.

## Quick Start

### Prerequisites
- **Docker Desktop** installed and running
- **Docker Compose** (usually included with Docker Desktop)

### Running with Docker

```bash
# Start the web interface
./run_docker.sh

# Or manually with docker-compose
docker-compose up --build
```

The web interface will be available at: **http://localhost:8501**

## Docker Components

### Dockerfile
The main container configuration file that:
- Uses Python 3.9 slim image for smaller size
- Installs system dependencies (gcc, g++)
- Installs Python packages from requirements.txt
- Creates a non-root user for security
- Exposes port 8501 for the web interface
- Sets the default command to run the Streamlit app

### docker-compose.yml
Orchestrates the container setup:
- Builds the image from Dockerfile
- Maps port 8501 to host
- Mounts volumes for development and data
- Sets environment variables
- Configures container behavior

### .dockerignore
Specifies files to exclude from the Docker build context:
- Git files (.git, .gitignore)
- Python cache files (__pycache__, *.pyc)
- Documentation files (*.md)
- Development files (.vscode, .idea)
- Data and output files (*.png, *.avi, *.csv)
- Experimental files (neat-*.py)

### run_docker.sh
A convenient script that:
- Checks if Docker is running
- Creates necessary directories
- Builds the Docker image
- Starts the container
- Provides helpful information

## Container Architecture

### Base Image
- **python:3.9-slim**: Lightweight Python image
- **System Dependencies**: gcc, g++ for compiled extensions
- **Security**: Non-root user (appuser)

### Application Structure
```
/app/
├── core/           # Core simulation modules
├── evolution/      # Genetic algorithm
├── visualization/ # Plotting tools
├── analysis/       # Research tools
├── examples/       # Usage examples
├── web_app.py      # Streamlit application
├── requirements.txt # Python dependencies
└── Dockerfile     # Container configuration
```

### Port Mapping
- **Host Port**: 8501
- **Container Port**: 8501
- **Protocol**: HTTP

### Volume Mounts
- **Current Directory**: `.:/app` (for development)
- **Data Directory**: `./data:/app/data` (for data persistence)

## Usage Examples

### Basic Usage
```bash
# Start the web interface
./run_docker.sh

# Access at http://localhost:8501
```

### Development Mode
```bash
# Run with volume mounting for live code changes
docker-compose up --build

# Make changes to code and see them reflected immediately
```

### Custom Port
```bash
# Run on a different port
docker-compose up --build -p 8080:8501

# Access at http://localhost:8080
```

### Background Mode
```bash
# Run in background
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Interactive Shell
```bash
# Run container with interactive shell
docker-compose run --rm grn-simulation bash

# Inside container, run commands like:
python examples/run_simulation.py
python evolution/main_ga.py
```

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check Docker status
docker info

# Check available ports
netstat -an | grep 8501

# Check container logs
docker-compose logs
```

#### Import Errors
```bash
# Rebuild container
docker-compose down
docker-compose up --build

# Check if all files are copied
docker-compose run --rm grn-simulation ls -la
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Increase memory/CPU limits in docker-compose.yml
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x run_docker.sh

# Check user permissions in container
docker-compose run --rm grn-simulation whoami
```

### Debugging

#### Container Inspection
```bash
# Enter running container
docker exec -it grn-simulation bash

# Check Python environment
python -c "import sys; print(sys.path)"

# Check installed packages
pip list
```

#### Build Debugging
```bash
# Build with verbose output
docker-compose build --progress=plain

# Check build context
docker-compose build --no-cache
```

#### Network Debugging
```bash
# Check port binding
docker port grn-simulation

# Test connectivity
curl http://localhost:8501
```

## Advanced Configuration

### Custom Environment Variables
```yaml
# In docker-compose.yml
environment:
  - PYTHONPATH=/app
  - PYTHONUNBUFFERED=1
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

### Health Checks
```yaml
# In docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Multi-stage Builds
```dockerfile
# For production optimization
FROM python:3.9-slim as builder
# Build stage...

FROM python:3.9-slim as runtime
# Runtime stage...
```

## Production Deployment

### Docker Registry
```bash
# Tag image for registry
docker tag grn-simulation:latest your-registry/grn-simulation:latest

# Push to registry
docker push your-registry/grn-simulation:latest
```

### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml grn-simulation
```

### Kubernetes
```yaml
# Create deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grn-simulation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grn-simulation
  template:
    metadata:
      labels:
        app: grn-simulation
    spec:
      containers:
      - name: grn-simulation
        image: grn-simulation:latest
        ports:
        - containerPort: 8501
```

## Best Practices

### Security
- Use non-root user in container
- Keep base image updated
- Scan for vulnerabilities
- Limit container capabilities

### Performance
- Use multi-stage builds
- Optimize layer caching
- Minimize image size
- Use appropriate base images

### Development
- Use volume mounts for live development
- Keep Dockerfile simple
- Document build process
- Use .dockerignore effectively

### Maintenance
- Regular base image updates
- Security patches
- Dependency updates
- Performance monitoring

## References

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Streamlit Docker**: https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-using-docker
