#!/usr/bin/env bash

# TRIKUSEC_LYNIS_API_URL is used for certificate download and API operations
TRIKUSEC_LYNIS_UPLOAD_SERVER={{ trikusec_lynis_upload_server }}
TRIKUSEC_CERT_TMP=/tmp/trikusec.crt
TRIKUSEC_LICENSEKEY={{ licensekey }}

if [ ! -f /etc/debian_version ]; then
    echo "This script is only compatible with Debian-based systems."
    exit 1
fi

# If user is not root, use sudo if available
if [ $(id -u) -ne 0 ]; then
    if [ -x "$(command -v sudo)" ]; then
        SUDO=sudo
    else
        echo "Please run this script as root or install sudo."
        exit 1
    fi
fi

# Check if the server is reachable and has a valid certificate
curl -s "https://${TRIKUSEC_LYNIS_UPLOAD_SERVER}" -o /dev/null
if [ $? -ne 0 ]; then
    echo "Server certificate is self-signed. Adding it to the trusted certificates."
    # Check if openssl and ca-certificates are installed
    if [ ! -x "$(command -v openssl)" ] || [ ! -x "$(command -v update-ca-certificates)" ]; then
        echo "openssl or ca-certificates are not installed. Installing them..."
        ${SUDO} apt-get update && ${SUDO} apt-get install -y openssl ca-certificates
    fi
    
    openssl s_client -showcerts -connect "${TRIKUSEC_LYNIS_UPLOAD_SERVER}" </dev/null 2>/dev/null | sed -n -e '/BEGIN\ CERTIFICATE/,/END\ CERTIFICATE/ p' > ${TRIKUSEC_CERT_TMP}
    ${SUDO} cp ${TRIKUSEC_CERT_TMP} /usr/local/share/ca-certificates/trikusec.crt
    ${SUDO} update-ca-certificates
    rm -f ${TRIKUSEC_CERT_TMP}
else
    echo "Server certificate is valid."
fi

# Update and install necessary packages
${SUDO} apt-get update
${SUDO} apt-get install -y curl lynis rkhunter auditd

# Get installed Lynis version
LYNIS_VERSION=$(lynis --version)

# If a custom profile file already exists, tell the user to remove it
if [ -f /etc/lynis/custom.prf ]; then
    echo "A custom profile file already exists. Please remove it before running this script."
    exit 1
fi

# Create custom profile file if it doesn't exist
${SUDO} touch /etc/lynis/custom.prf

# Check and generate host identifiers if needed
# Host identifiers (hostid and hostid2) are used by Lynis to uniquely identify systems
# Reference: https://cisofy.com/documentation/lynis/
# In some environments (e.g., Docker containers), host identifiers may not be automatically generated
# If they are empty, we need to generate them manually
echo "Checking host identifiers..."
HOSTIDS_OUTPUT=$(lynis show hostids 2>/dev/null || echo "")
# Extract hostid and hostid2 values from the output
HOSTID_VALUE=$(echo "$HOSTIDS_OUTPUT" | grep -E "^hostid[[:space:]]*:" | sed 's/.*:[[:space:]]*//' | tr -d '[:space:]' || echo "")
HOSTID2_VALUE=$(echo "$HOSTIDS_OUTPUT" | grep -E "^hostid2[[:space:]]*:" | sed 's/.*:[[:space:]]*//' | tr -d '[:space:]' || echo "")

if [ -z "$HOSTID_VALUE" ] || [ -z "$HOSTID2_VALUE" ]; then
    echo "Host identifiers are empty. Generating new identifiers..."
    # Create custom profile file if it doesn't exist (required for lynis configure settings)
    ${SUDO} mkdir -p /etc/lynis
    ${SUDO} touch /etc/lynis/custom.prf
    # Generate host identifiers using random data
    # hostid: 40 characters (SHA1 hash)
    # hostid2: 64 characters (SHA256 hash)
    # Reference: https://cisofy.com/documentation/lynis/
    ${SUDO} lynis configure settings hostid=$(head -c 64 /dev/random | sha1sum | awk '{print $1}'):hostid2=$(head -c 64 /dev/random | sha256sum | awk '{print $1}')
    echo "Host identifiers generated successfully."
else
    echo "Host identifiers already exist."
fi


#
# Configure Lynis custom configuration by command
#
# Configure upload settings: enable upload, set license key, and upload server endpoint

# Bugfix: lynis configure does not work correctly with :port in the upload server URL
# so we need to set the configuration manually
echo "upload-server=${TRIKUSEC_LYNIS_UPLOAD_SERVER}/api/lynis" >> /etc/lynis/custom.prf

${SUDO} lynis configure settings upload=yes:license-key=${TRIKUSEC_LICENSEKEY}:upload-server=${TRIKUSEC_LYNIS_UPLOAD_SERVER}/api/lynis auditor=TrikuSec

# If lynis version is older than 3.0.0, add test_skip_always=CRYP-7902 to the custom profile
# Extract major version number for comparison
LYNIS_MAJOR=$(echo "$LYNIS_VERSION" | awk -F. '{print $1}')
# Add test skip if major version is less than 3 (i.e., version < 3.0.0)
if [ "$LYNIS_MAJOR" -lt 3 ]; then
    ${SUDO} lynis configure settings test_skip_always=CRYP-7902
fi

# First audit
lynis audit system --upload --quick

