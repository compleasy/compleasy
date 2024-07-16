# nginx/generate-certs.sh

#!/bin/sh

CERT_DIR="/etc/nginx/certs"
CERT_FILE="$CERT_DIR/cert.pem"
KEY_FILE="$CERT_DIR/key.pem"

# Create the certificates directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate certificates if they do not exist
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed certificates..."

    openssl req -new -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

    echo "Certificates generated at $CERT_DIR/"
else
    echo "Certificates already exist at $CERT_DIR/"
fi

# Execute the original Nginx entrypoint
exec "$@"
