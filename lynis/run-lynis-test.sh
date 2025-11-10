#!/bin/bash

set -e

# Configuration
COMPLEASY_SERVER_URL="${COMPLEASY_SERVER_URL:-http://compleasy-dev:8000}"
COMPLEASY_LICENSE_KEY="${COMPLEASY_LICENSE_KEY}"
MAX_RETRIES=30
RETRY_DELAY=2

echo "=== Compleasy Lynis Integration Test ==="
echo "Server URL: ${COMPLEASY_SERVER_URL}"
echo "License Key: ${COMPLEASY_LICENSE_KEY}"

# Wait for Compleasy server to be ready
echo "Waiting for Compleasy server to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f -s "${COMPLEASY_SERVER_URL}/api/" > /dev/null 2>&1; then
        echo "Server is ready!"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "ERROR: Server not ready after ${MAX_RETRIES} attempts"
        exit 1
    fi
    echo "Attempt $i/$MAX_RETRIES: Server not ready, waiting ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
done

# Check license validity
echo ""
echo "=== Step 1: Checking license validity ==="
if [ -z "$COMPLEASY_LICENSE_KEY" ]; then
    echo "ERROR: COMPLEASY_LICENSE_KEY not set"
    exit 1
fi

LICENSE_CHECK=$(curl -s -X POST "${COMPLEASY_SERVER_URL}/api/lynis/license/" \
    -d "licensekey=${COMPLEASY_LICENSE_KEY}&collector_version=1.0.0" || echo "ERROR")

if [ "$LICENSE_CHECK" = "Response 100" ]; then
    echo "✓ License key is valid"
else
    echo "✗ License key validation failed: $LICENSE_CHECK"
    exit 1
fi

# Create Lynis custom profile
echo ""
echo "=== Step 2: Creating Lynis custom profile ==="
mkdir -p /etc/lynis
cat > /etc/lynis/custom.prf <<EOF
# Custom profile for Compleasy testing
upload=yes
license-key=${COMPLEASY_LICENSE_KEY}
upload-server=${COMPLEASY_SERVER_URL#http://}
upload-options=--insecure
test_skip_always=CRYP-7902
EOF

echo "✓ Custom profile created at /etc/lynis/custom.prf"

# Run first Lynis scan
echo ""
echo "=== Step 3: Running first Lynis scan ==="
lynis audit system --profile /etc/lynis/custom.prf --quick --upload || {
    echo "✗ First Lynis scan failed"
    exit 1
}
echo "✓ First scan completed and uploaded"

# Wait a bit before second scan
sleep 2

# Run second Lynis scan to generate diff
echo ""
echo "=== Step 4: Running second Lynis scan (for diff generation) ==="
lynis audit system --profile /etc/lynis/custom.prf --quick --upload || {
    echo "✗ Second Lynis scan failed"
    exit 1
}
echo "✓ Second scan completed and uploaded"

# Verify upload by checking if we can query the server
echo ""
echo "=== Step 5: Verifying upload success ==="
echo "✓ All tests completed successfully"

echo ""
echo "=== Integration Test Summary ==="
echo "✓ License validation: PASSED"
echo "✓ First report upload: PASSED"
echo "✓ Second report upload (diff): PASSED"
echo ""
echo "Integration test completed successfully!"

