# 🧩 BC Data Collection Utility

This project provides a Python utility to programmatically access and retrieve data from **Microsoft Dynamics 365 Business Central (BC)** through two API endpoints: the **ODataV4** endpoint and the **API v2.0** endpoint.  

It simplifies authentication and data retrieval using reusable classes (`BCTokenClient` and `BCHandler`), designed for integration in environments such as **Airflow pipelines**.

---

## 📘 Overview

In this notebook and module, we demonstrate how to:
1. Authenticate and retrieve a token using `BCTokenClient`.
2. Use that token to access BC data via the `BCHandler` class.

Business Central exposes two main data endpoints:

---

### 1️⃣ ODataV4 Endpoint

**Base URL:** `https://api.businesscentral.dynamics.com/v2.0/{tenant_id}/{env_name}/ODataV4/`
- Standards-based **OData 4.0** protocol for reading, filtering, and updating data entities.
- Commonly used for **direct access to Business Central pages/tables** published as web services.
- Supports XML and JSON payloads.

> ✅ **Use this** when you need direct access to tables/pages you’ve published as web services.

---

### 2️⃣ API v2 Endpoint

**Base URL:** `https://api.businesscentral.dynamics.com/v2.0/{tenant_id}/{env_name}/api/v2.0/`
- Standardized, **versioned REST API layer** built by Microsoft.
- Uses OData v4 under the hood but provides **stable and predictable structures** for integrations.
- Ideal for **programmatic applications, connectors, and third-party systems**.

> ✅ **Use this** when building integrations or apps that need versioned, standardized APIs.

---
## 🧩 Repository Structure
```bash
bc_api/
├── __init__.py
├── authenticator.py     # Contains BCTokenClient class
└── handler.py           # Contains BCHandler, BCMetaData, BCData classes
```

---
## 🧠 Utility Classes

The BC API utility is composed of the following components:

### 1. `BCTokenClient`

Defined in: `bc_api/authenticator.py`

Handles authentication by retrieving the Bearer token required for API access.
```python
client = BCTokenClient(base_url="192.168.70.231:4413")
token = client.get_token(username="user@domain.com", password="mypassword")
```

**Key Features:**

- Validates credentials.
- Handles connection and timeout errors gracefully.
- Returns the authentication token for subsequent API calls.

### 2. `BCHandler`

Defined in: `bc_api/handler.py`

Handles data requests from BC using a valid token. Supports both ODataV4 and API v2 endpoints.

```python
handler = BCHandler(
    tenant_id="your-tenant-id",
    env_name="Production",
    endpoint_type="v2",
    token=token
)

companies = handler.get_companies()
metadata = handler.get_metadata()
```

**Key Features:**

- Dynamically switches between ODataV4 and v2 endpoint modes.
- Retrieves metadata ($metadata) and company lists.
- Supports flexible data extraction from any BC table or API entity.

### 3. BCMetaData and BCData

These classes process and normalize responses from BC. Only the `get_metadata` and `get_companies` methods currently return outputs that are inside the `BCMetaData` and `BCData`, respectively.

| Class | Purpose | Attributes |
| ----- | ------- | ------ |
| BCMetaData | Parses and flattens XML metadata returned by `$metadata` endpoint | `.raw`, `.json`, `.flat_json` |
| BCData | Processes JSON data from tables or API endpoints	| `.raw`, `.flat_json` |

**Example:**
```python
metadata = handler.get_metadata()
print(metadata.flat_json[:5])  # Flattened metadata for inspection

companies = handler.get_companies()
print(companies.flat_json)     # Company list as JSON
```

---
> [!IMPORTANT] 
> - SSL verification is disabled (`verify=False`) for development purposes.
>   - Use proper SSL certificates in production.
> - Tokens expire periodically — regenerate them using `BCTokenClient`.
> - Metadata endpoints are XML-based (`$metadata`), while all other endpoints are JSON-based, whether for the `ODataV4` or `API v2` endpoint.