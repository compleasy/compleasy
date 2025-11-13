# API Endpoints

Complete reference for all API endpoints.

## Lynis Endpoints

### Upload Report

Upload a Lynis audit report.

**Endpoint:** `POST /api/lynis/upload/`

**Legacy:** `POST /api/v1/lynis/upload/`

**Request Format:** Form data

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `licensekey` | string | Yes | License key for authentication |
| `hostid` | string | Yes | Host identifier |
| `hostid2` | string | No | Secondary host identifier |
| `data` | string | Yes | Base64-encoded Lynis report data |

**Response:**

- `200 OK` - Report uploaded successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid license key

**Example:**

```bash
curl -X POST https://yourserver:3000/api/lynis/upload/ \
  -F "licensekey=your-license-key" \
  -F "hostid=server-01" \
  -F "data=$(base64 -w 0 /var/log/lynis-report.dat)"
```

### Check License

Validate a license key.

**Endpoint:** `POST /api/lynis/license/`

**Legacy:** `POST /api/v1/lynis/license/`

**Request Format:** Form data

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `licensekey` | string | Yes | License key to validate |
| `collector_version` | string | No | Lynis collector version |

**Response:**

- `200 OK` - Valid license (Response: `Response 100`)
- `401 Unauthorized` - Invalid license (Response: `Response 500`)

**Example:**

```bash
curl -X POST https://yourserver:3000/api/lynis/license/ \
  -F "licensekey=your-license-key" \
  -F "collector_version=3.0.0"
```

!!! important "Lynis Compatibility"
    These endpoints maintain compatibility with Lynis clients. The response format (`Response 100` / `Response 500`) is required for Lynis compatibility.

## Device Endpoints

### List Devices

Get a list of all devices.

**Endpoint:** `GET /api/devices/`

**Authentication:** Required (session or API key)

**Response:**

```json
{
  "devices": [
    {
      "id": 1,
      "hostid": "server-01",
      "licensekey": "xxx",
      "last_report": "2024-01-15T10:30:00Z",
      "compliance": 85.5
    }
  ]
}
```

### Get Device

Get details for a specific device.

**Endpoint:** `GET /api/devices/{id}/`

**Authentication:** Required

**Response:**

```json
{
  "id": 1,
  "hostid": "server-01",
  "licensekey": "xxx",
  "last_report": "2024-01-15T10:30:00Z",
  "compliance": 85.5,
  "warnings": [...],
  "suggestions": [...]
}
```

## Policy Endpoints

### List Policies

Get a list of all policy rules.

**Endpoint:** `GET /api/policies/rules/`

**Authentication:** Required

### Create Policy Rule

Create a new policy rule.

**Endpoint:** `POST /api/policies/rules/`

**Authentication:** Required

**Request:**

```json
{
  "test_id": "FILE-7524",
  "operator": "equals",
  "value": "640",
  "severity": "warning"
}
```

## Report Endpoints

### Get Device Reports

Get audit reports for a device.

**Endpoint:** `GET /api/devices/{id}/reports/`

**Authentication:** Required

**Response:**

```json
{
  "reports": [
    {
      "id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "compliance": 85.5,
      "warnings_count": 5,
      "suggestions_count": 12
    }
  ]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing authentication |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

## Next Steps

- [Authentication](authentication.md) - Learn about authentication
- [Examples](examples.md) - See code examples

