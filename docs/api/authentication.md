# API Authentication

Authentication methods for TrikuSec API.

## License Key Authentication

Lynis endpoints use license key authentication via form data.

### Upload Endpoint

```bash
curl -X POST https://yourserver:3000/api/lynis/upload/ \
  -F "licensekey=your-license-key" \
  -F "hostid=server-01" \
  -F "data=..."
```

### License Check Endpoint

```bash
curl -X POST https://yourserver:3000/api/lynis/license/ \
  -F "licensekey=your-license-key"
```

## Session Authentication

For web-based API access, use Django session authentication:

1. Login via web interface
2. Use session cookie in API requests

```bash
curl -X GET https://yourserver:3000/api/devices/ \
  -H "Cookie: sessionid=your-session-id"
```

## API Key Authentication

API key authentication (coming soon) for programmatic access.

## Security Best Practices

- **Use HTTPS** - Always use HTTPS in production
- **Protect License Keys** - Never expose license keys in logs or version control
- **Rotate Keys** - Regularly rotate license keys
- **Rate Limiting** - Be aware of rate limits on API endpoints

## Troubleshooting

### Invalid License Key

If you get `401 Unauthorized`:

1. Verify the license key is correct
2. Check that the license key exists in TrikuSec
3. Ensure the license key hasn't been revoked

### Connection Issues

If you can't connect:

1. Check server URL is correct
2. Verify firewall allows connections
3. Check SSL certificate (use `--insecure` for self-signed certs)

## Next Steps

- [Endpoints](endpoints.md) - See all available endpoints
- [Examples](examples.md) - Integration examples

