# Weather Data Pipeline — OpenWeatherMap + Azure

## Overview

This repository contains the code and documentation for a data pipeline that collects weather data (current conditions) for Brazilian state capitals using the OpenWeatherMap API and stores periodic snapshots in an Azure Storage Account via Azure Functions (Python).

The implemented solution provides:

* HTTP endpoints for manual data collection
* A Timer Trigger for automatic, scheduled collection
* JSON uploads to an Azure Blob Storage container named `weather-container`

> Note: The Azure Functions code is implemented using the **decorator-based Python model** (`func.FunctionApp`), also known as the Python v2 programming model.

---

## Current Project Status

* **Functions implemented and tested locally:** ✅

  * HTTP: `/api/collect/all` (CollectAllCapitals)
  * HTTP: `/api/hello` (test endpoint)
  * Timer: `AutoWeatherCollector` (automatic collection)
* **Storage:** ✅ JSON files successfully uploaded to Azure Blob Storage (`weather-container`)
* **Autonomous cloud execution:** ⚠️ **Not deployed** (cloud deployment not completed due to Azure subscription permission issues)

---

## Repository Structure

* `function_app.py` — Main Azure Functions implementation using `func.FunctionApp()`
* `requirements.txt` — Project dependencies
* `.gitignore` — Recommended exclusions (including `local.settings.json`)
* `docs/` — Additional documentation (optional)
* `README.md` — This file

---

## Execution Details (Based on Current Code)

### Implementation Model

* This project uses the **Azure Functions Python decorator-based model**.
* It does **not** use the classic per-function folder structure (`<function_name>/__init__.py` + `function.json`).
* Functions defined in the code:

  * `CollectAllCapitals` — HTTP-triggered function (`route="collect/all"`)
  * `AutoWeatherCollector` — Timer-triggered function
  * `hello` — Simple HTTP test endpoint

### Environment Variables (Exact Names Used in Code)

The application reads the following environment variables. The names are **case-sensitive** and must match exactly:

* `OpenWeather_ApiKey` — OpenWeatherMap API key
* `AzureWebJobsStorage` — Azure Storage Account connection string (used directly by `BlobServiceClient.from_connection_string`)

> Note: The code does **not** use `AZURE_STORAGE_CONNECTION_STRING`; the Storage connection relies entirely on `AzureWebJobsStorage`.

---

## HTTP Endpoints

* `GET /api/hello`

  * Test endpoint
  * Returns: `Azure Functions está funcionando!`

* `GET /api/collect/all`

  * Triggers synchronous collection of all configured Brazilian capitals
  * Returns a JSON summary with per-city status, blob path, and basic weather fields

---

## Timer Trigger Configuration

* **Function name:** `AutoWeatherCollector`
* **CRON schedule:** `0 */10 * * * *`
* **Execution frequency:** Every 10 minutes

The timer runs independently of HTTP requests and stores its output in the same Blob Storage container.

---

## Storage Behavior

* **Target container:** `weather-container` (must exist prior to execution)
* **Blob path patterns:**

  * HTTP trigger:

    ```
    capitais-batch/{city_formatted}/{YYYYMMDD_HHMMSS}.json
    ```
  * Timer trigger:

    ```
    timer-auto/{city_formatted}/{YYYYMMDD_HHMMSS}.json
    ```

### Stored JSON Structure

Each blob contains a snapshot similar to:

```json
{
  "extraction_timestamp": "2025-01-20T15:30:00Z",
  "source_system": "OpenWeatherMap",
  "city_requested": "Brasília",
  "weather_data": { /* raw OpenWeatherMap API response */ }
}
```

**Timestamp behavior:**

* Blob filenames use `datetime.now()` (local time of the execution host)
* The `extraction_timestamp` field uses `datetime.utcnow()` with `Z` suffix (UTC)

---

## List of Capitals

The pipeline collects data for 27 Brazilian capitals (one per federative unit, including the Federal District). The list is hardcoded in the application (`capitais_brasil`) and must be updated in code if changes are required.

---

## API Rate Limiting Considerations

* The code enforces a delay of `1.2` seconds between API calls using `time.sleep(1.2)`.
* This is intended to reduce the risk of exceeding OpenWeatherMap rate limits.
* Actual limits depend on the OpenWeatherMap subscription plan (Free vs. Paid).

---

## Dependencies

Required packages (as listed in `requirements.txt`):

```
azure-functions
azure-storage-blob
requests
```

Recommended Python version: **3.10+** (compatible with the Azure Functions Python runtime).

---

## Local Execution

### 1. Create and Activate a Virtual Environment (example: Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Local Settings

Create a `local.settings.json` file (do **not** commit it):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your-storage-connection-string>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "OpenWeather_ApiKey": "<your-openweathermap-api-key>"
  }
}
```

### 3. Run the Function App Locally

```bash
func start
```

### 4. Test Endpoints

* `http://localhost:7071/api/hello`
* `http://localhost:7071/api/collect/all`

Verify that JSON files are being created in the `weather-container` container.

---

## Security Notes

* **HTTP authorization:** The `FunctionApp` is initialized with `http_auth_level=func.AuthLevel.ANONYMOUS`, meaning all HTTP endpoints are publicly accessible.
* **Secrets management:** Never commit API keys or connection strings. Use Application Settings in Azure and/or Azure Key Vault for production deployments.

---

## Deployment Notes

* Deployment can be performed using:

```bash
func azure functionapp publish <FUNCTION_APP_NAME>
```

* The deploying identity must have sufficient permissions (Owner or Contributor) on the Azure subscription or resource group.
* Cloud deployment is currently not completed due to permission constraints.

---

## Final Notes

* Ensure the `weather-container` container exists before execution.
* Confirm that `AzureWebJobsStorage` points to the correct Storage Account.
* Review OpenWeatherMap rate limits when adjusting the timer schedule or the number of cities.
* Timestamp handling intentionally mixes local time (filenames) and UTC (payload metadata), as implemented in the code.

---

## License

Add an appropriate license (e.g., MIT or Apache-2.0) before publishing the repository.
