# Weather Data Pipeline - Azure + OpenWeatherMap

[![Azure Functions](https://img.shields.io/badge/Azure-Functions-0089D6?logo=microsoft-azure)](https://azure.microsoft.com/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenWeatherMap](https://img.shields.io/badge/API-OpenWeatherMap-orange)](https://openweathermap.org/)
[![Azure Storage](https://img.shields.io/badge/Storage-Azure_Blob-0089D6)](https://azure.microsoft.com/services/storage/)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Execution](#local-execution)
- [Data Structure](#data-structure)
- [Available Endpoints](#available-endpoints)
- [Monitoring and Logs](#monitoring-and-logs)
- [Challenges and Solutions](#challenges-and-solutions)
- [Next Steps](#next-steps)
- [License](#license)

---

## Overview

This project implements a **real-time data pipeline** that automatically collects weather information from all 27 Brazilian state capitals using the OpenWeatherMap API. Data is processed and stored in JSON format in Azure Blob Storage, creating a data lake for future analysis.

**Current Status:** The pipeline is fully functional and runs successfully in local development mode. All features work as intended, including automated data collection via timer trigger and manual collection via HTTP endpoints. Cloud deployment to Azure Function App was attempted but not completed due to Azure subscription permission challenges.

### Project Goals

- ✅ Automate weather data collection at regular intervals
- ✅ Store historical data for temporal analysis
- ✅ Create a scalable and serverless infrastructure
- ✅ Implement data engineering best practices (logging, error handling, rate limiting)

---

## Architecture

```
┌─────────────────────┐
│  Timer Trigger      │
│  (Every 10 min)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Azure Function     │
│  (Python 3.10+)     │
└──────────┬──────────┘
           │
           ├──────────────────┐
           │                  │
           ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│ OpenWeatherMap  │  │  Azure Blob     │
│     API         │  │    Storage      │
└─────────────────┘  └─────────────────┘
```

### Data Flow

1. **Automatic Trigger**: Timer trigger activates the function every 10 minutes
2. **Data Collection**: HTTP requests to OpenWeatherMap API (27 capitals)
3. **Processing**: Data enrichment with metadata (timestamp, source, etc.)
4. **Storage**: Upload to Azure Blob Storage in hierarchical structure
5. **Logging**: Complete logging of all operations for monitoring

---

## Features

### 🔄 Automated Collection
- **Timer Trigger**: Automatic execution every 10 minutes
- **Rate Limiting**: Delay implementation (1.2s) to respect API limits
- **Retry Logic**: Robust error handling for connection issues

### 📊 HTTP Endpoints

#### 1. `GET /api/hello`
Test endpoint to verify function operation.

**Response:**
```
Azure Functions is working!
```

#### 2. `GET /api/collect/all`
Manual data collection from all capitals on demand.

**JSON Response:**
```json
{
  "total_capitais": 27,
  "coletadas_com_sucesso": 27,
  "com_erro": 0,
  "timestamp": "2025-01-21T18:30:00Z",
  "resultados": [...]
}
```

### 🗂️ Storage Structure

```
capitals/
├── capitais-batch/
│   ├── rio-branco/
│   │   └── 20250121_183000.json
│   ├── brasilia/
│   │   └── 20250121_183002.json
│   └── ...
└── timer-auto/
    ├── sao-paulo/
    │   ├── 20250121_180000.json
    │   └── 20250121_181000.json
    └── ...
```


---

## Tech Stack

| Technology | Version | Purpose |
|------------|--------|-----------|
| **Python** | 3.10+ | Main language |
| **Azure Functions** | v4 | Serverless compute |
| **Azure Blob Storage** | StorageV2 | Data lake |
| **OpenWeatherMap API** | 2.5 | Weather data source |
| **Requests** | Latest | HTTP client |
| **azure-storage-blob** | Latest | Azure Storage SDK |

---

## Prerequisites

### Accounts and Credentials

1. **OpenWeatherMap Account**
   - Create account at [openweathermap.org](https://openweathermap.org)
   - Generate API Key in the dashboard
   - Free plan allows 60 requests/minute

2. **Microsoft Azure Account**
   - Create account at [portal.azure.com](https://portal.azure.com)
   - Configure Resource Group
   - Create Storage Account

### Development Tools

```bash
# Python 3.10 or higher
python --version

# Azure Functions Core Tools
func --version

# Visual Studio Code (recommended)
# + Azure Functions Extension
```

---

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/periclesrmessias/weather-data-pipeline.git
cd weather-data-pipeline
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt:**
```txt
azure-functions
azure-storage-blob
requests
```

### 4. Configure Azure Storage

1. Access the [Azure Portal](https://portal.azure.com)
2. Navigate to your Storage Account
3. Go to **Security + Networking** → **Access Keys**
4. Copy the **Connection String** from Key1
5. Create a container named `weather-container`


### 5. Configure Environment Variables

Create the `local.settings.json` file:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "YOUR_CONNECTION_STRING_HERE",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "OpenWeather_ApiKey": "YOUR_API_KEY_HERE"
  }
}
```

> ⚠️ **IMPORTANT**: Never commit this file! It's already in `.gitignore`

![Project Structure](https://github.com/periclesrmessias/weather_data/blob/main/images/files.png?raw=true)

---

## Local Execution

### Start the Function

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start Azure Functions runtime
func start
```

![Function Execution Logs](https://github.com/periclesrmessias/weather_data/blob/main/images/func-start.png?raw=true)

### Test Endpoints

**Basic test:**
```bash
curl http://localhost:7071/api/hello
```

**Manual collection:**
```bash
curl http://localhost:7071/api/collect/all
```

### Verify Timer Trigger

The timer is configured to execute every 10 minutes (`0 */10 * * * *`). 

You'll see logs like:
```
[2025-01-21T18:00:00] 🔄 TIMER TRIGGERED: Starting automatic collection...
[2025-01-21T18:00:01] ⏳ Timer collecting: Rio Branco
[2025-01-21T18:00:03] ✅ Timer: Rio Branco saved
...
[2025-01-21T18:03:25] 🏁 Timer completed: 27/27 capitals
```

---

## Data Structure

### Example of Stored JSON File

```json
{
  "extraction_timestamp": "2025-01-21T18:30:00Z",
  "source_system": "OpenWeatherMap",
  "city_requested": "São Paulo",
  "weather_data": {
    "coord": {
      "lon": -46.6361,
      "lat": -23.5475
    },
    "weather": [
      {
        "id": 800,
        "main": "Clear",
        "description": "clear sky",
        "icon": "01d"
      }
    ],
    "main": {
      "temp": 28.5,
      "feels_like": 30.2,
      "temp_min": 26.0,
      "temp_max": 31.0,
      "pressure": 1013,
      "humidity": 65
    },
    "wind": {
      "speed": 3.5,
      "deg": 180
    },
    "dt": 1737486000,
    "name": "São Paulo"
  }
}
```

### Main Fields

| Field | Type | Description |
|-------|------|-----------|
| `extraction_timestamp` | ISO 8601 | Collection time (UTC) |
| `source_system` | String | Always "OpenWeatherMap" |
| `city_requested` | String | Requested city name |
| `weather_data` | Object | Complete API response |

---

## Available Endpoints

### 1. Health Check

```http
GET /api/hello
```

**Response:**
```
Status: 200 OK
Azure Functions is working!
```

### 2. Batch Manual Collection

```http
GET /api/collect/all
```

**Response:**
```json
{
  "total_capitais": 27,
  "coletadas_com_sucesso": 27,
  "com_erro": 0,
  "timestamp": "2025-01-21T18:30:00Z",
  "resultados": [
    {
      "cidade": "São Paulo",
      "status": "sucesso",
      "blob_path": "capitais-batch/sao-paulo/20250121_183000.json",
      "temperatura": 28.5,
      "clima": "clear sky"
    },
    ...
  ]
}
```

---

## Monitoring and Logs

### Execution Logs

The function generates detailed logs for all operations:

```python
logging.info(f"Collecting data from: {city}")
logging.info(f"✅ {city} saved at: {blob_name}")
logging.error(f"❌ API error for {city}: {error}")
```

### Available Metrics

- Total successful executions
- Error rate per capital
- Average execution time
- Volume of stored data

### Visualization in Azure

1. Access the **Azure Portal**
2. Navigate to **Storage Account** (e.g., `apiweatherdata`) → **Containers** → `capitals`
3. Explore the hierarchical folder structure

![Azure Container](https://github.com/periclesrmessias/weather_data/blob/main/images/weather-container.png?raw=true)

4. Download individual JSON files for inspection

---

## Challenges and Solutions

### 1. **Character Encoding**

**Problem:** City names with accents (São Paulo, Brasília, Maceió, Belém)

**Solution:**
```python
cidade_formatada = cidade.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c').replace('ó', 'o').replace('é', 'e')
# "São Paulo" → "sao-paulo"
# "Maceió" → "maceio"
```

### 2. **VS Code Creating Duplicate Functions**

**Problem:** VS Code automatically created a duplicate `getweather` function during project initialization

**Solution:**
- Removed the timer trigger temporarily to test HTTP trigger in isolation
- Consolidated all functions into a single `function_app.py`
- Tested each trigger independently before combining them

### 3. **API Rate Limiting**

**Problem:** OpenWeatherMap limits 60 requests/minute on Free plan

**Solution:**
```python
time.sleep(1.2)  # Ensures maximum 50 req/min
```

### 3. **Credentials Management**

**Problem:** Need to protect API Keys and Connection Strings

**Solution:**
- Use of `local.settings.json` (excluded from Git)
- Environment variables via `os.environ.get()`
- Properly configured `.gitignore`

### 4. **Azure Permissions**

**Problem:** Insufficient permissions for initial deployment

**Solution:**
- Configuration of "Owner" role in Resource Group
- Use of Microsoft organizational account (recommended)
- Acceptance of collaborator invitations

---

## Next Steps

### Short Term

- [ ] **Cloud Deploy**: Resolve Azure subscription permissions and deploy to Azure Function App
- [ ] **Timer Optimization**: Adjust timer trigger schedule based on data analysis needs
- [ ] **CI/CD Pipeline**: Implement GitHub Actions for automated deployment
- [ ] **Unit Tests**: Code coverage with pytest
- [ ] **API Documentation**: Swagger/OpenAPI specification

### Medium Term

- [ ] **Data Warehouse**: Implement Azure SQL Database or Synapse Analytics
- [ ] **Data Transformation**: ETL pipeline with Azure Data Factory
- [ ] **Visualization**: Dashboard in Power BI or Grafana
- [ ] **Alerts**: Notifications for extreme weather conditions

### Long Term

- [ ] **Machine Learning**: Predictive models for temperature/precipitation
- [ ] **Custom API**: REST endpoint for historical data queries
- [ ] **Geographic Expansion**: Include non-capital cities
- [ ] **Multiple Sources**: Integration with INMET, CPTEC, etc.

---

## License

This project is under the MIT License. See the [LICENSE](LICENSE) file for more details.
