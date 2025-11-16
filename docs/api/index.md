# API Reference

Complete API reference for TrikuSec.

## Overview

TrikuSec provides REST API endpoints for:

- Uploading audit reports
- License key validation
- Device management
- Policy management
- Report retrieval

## Base URL

```
https://yourserver:3000/api
```

## API Versioning

TrikuSec supports API versioning:

- **Versioned API**: `/api/v1/lynis/...`
- **Legacy API**: `/api/lynis/...` (for backward compatibility)

Both endpoints route to the same views.

## Authentication

Currently, API endpoints use license key authentication. See [Authentication](authentication.md) for details.

## Endpoints

- **[API Endpoints](endpoints.md)** - Complete list of endpoints
- **[Authentication](authentication.md)** - Authentication methods
- **[Examples](examples.md)** - Code examples and use cases

## Rate Limiting

API endpoints are rate-limited to prevent abuse. See configuration for details.

## Response Formats

### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Next Steps

- [Endpoints](endpoints.md) - Detailed endpoint documentation
- [Examples](examples.md) - Integration examples

