# API Examples

Code examples and integration patterns for TrikuSec API.

## Python Examples

### Upload Report

```python
import requests
import base64

# Read Lynis report
with open('/var/log/lynis-report.dat', 'rb') as f:
    report_data = base64.b64encode(f.read()).decode('utf-8')

# Upload to TrikuSec
response = requests.post(
    'https://yourserver:3000/api/lynis/upload/',
    data={
        'licensekey': 'your-license-key',
        'hostid': 'server-01',
        'data': report_data
    },
    verify=False  # For self-signed certificates
)

if response.status_code == 200:
    print('Report uploaded successfully')
else:
    print(f'Error: {response.text}')
```

### Check License

```python
import requests

response = requests.post(
    'https://yourserver:3000/api/lynis/license/',
    data={
        'licensekey': 'your-license-key',
        'collector_version': '3.0.0'
    },
    verify=False
)

if response.text == 'Response 100':
    print('License is valid')
else:
    print('License is invalid')
```

### Get Devices

```python
import requests

# Using session authentication
session = requests.Session()
session.post(
    'https://yourserver:3000/login/',
    data={'username': 'admin', 'password': 'password'}
)

response = session.get('https://yourserver:3000/api/devices/')
devices = response.json()

for device in devices['devices']:
    print(f"Device: {device['hostid']}, Compliance: {device['compliance']}%")
```

## Bash Examples

### Upload Report Script

```bash
#!/bin/bash

LICENSE_KEY="your-license-key"
SERVER="https://yourserver:3000"
HOSTID=$(hostname)

# Read and encode report
REPORT_DATA=$(base64 -w 0 /var/log/lynis-report.dat)

# Upload report
curl -k -X POST "${SERVER}/api/lynis/upload/" \
  -F "licensekey=${LICENSE_KEY}" \
  -F "hostid=${HOSTID}" \
  -F "data=${REPORT_DATA}"

if [ $? -eq 0 ]; then
    echo "Report uploaded successfully"
else
    echo "Failed to upload report"
    exit 1
fi
```

### Check License Script

```bash
#!/bin/bash

LICENSE_KEY="your-license-key"
SERVER="https://yourserver:3000"

RESPONSE=$(curl -k -s -X POST "${SERVER}/api/lynis/license/" \
  -F "licensekey=${LICENSE_KEY}")

if [ "$RESPONSE" = "Response 100" ]; then
    echo "License is valid"
    exit 0
else
    echo "License is invalid"
    exit 1
fi
```

## Integration with Lynis

### Custom Lynis Profile

Add to `/etc/lynis/custom.prf`:

```ini
upload=yes
license-key=your-license-key
upload-server=yourserver:3000/api/lynis
upload-options=--insecure
```

### Automated Upload

Add to cron:

```bash
# Run audit and upload daily at 2 AM
0 2 * * * /usr/sbin/lynis audit system --upload --quick
```

## Error Handling

### Python Error Handling

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        'https://yourserver:3000/api/lynis/upload/',
        data={'licensekey': 'key', 'hostid': 'host', 'data': '...'},
        timeout=30,
        verify=False
    )
    response.raise_for_status()
except RequestException as e:
    print(f'Request failed: {e}')
except Exception as e:
    print(f'Unexpected error: {e}')
```

## Best Practices

- **Error Handling** - Always handle errors gracefully
- **Retry Logic** - Implement retry logic for transient failures
- **Logging** - Log API calls for debugging
- **Timeouts** - Set appropriate timeouts
- **SSL Verification** - Use proper SSL certificates in production

## Next Steps

- [Endpoints](endpoints.md) - Complete endpoint reference
- [Authentication](authentication.md) - Authentication details

