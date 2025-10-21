# Database Setup Guide

## Prerequisites
- macOS with Homebrew installed
- Poetry for Python dependency management

## Installation Steps

### 1. Install PostgreSQL
```bash
brew install postgresql@15
```

### 2. Start PostgreSQL Service
```bash
brew services start postgresql@15
```

### 3. Add PostgreSQL to PATH
```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

### 4. Create Database
```bash
createdb sensor_metrics
```

### 5. Install Python Dependencies
```bash
poetry install
```

### 6. Set Environment Variables
```bash
# Replace 'your_username' with your actual system username
export DB_USER=$(whoami)
export DB_PASSWORD=""
export DB_NAME=sensor_metrics
```

### 7. Initialize Database Schema
```bash
poetry run python scripts/init_database.py
```

### 8. Start API Server
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Quick Start Script
Save this as `start.sh`:
```bash
#!/bin/bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
export DB_USER=$(whoami)
export DB_PASSWORD=""
export DB_NAME=sensor_metrics
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verification
Test the API:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","database":"connected","timestamp":"..."}
```

## Troubleshooting
- If PostgreSQL connection fails, ensure the service is running: `brew services list | grep postgresql`
- If database doesn't exist, create it: `createdb sensor_metrics`
- If schema initialization fails, check environment variables are set correctly
