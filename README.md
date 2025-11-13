# Compleasy

> [!WARNING]
> This project is still in development and should NOT be used in production.

**Compleasy** is a centralized Linux server auditing and compliance management platform built on [Lynis](https://cisofy.com/lynis/). It collects, stores, and analyzes security audit reports from multiple Linux servers in one place, enabling centralized monitoring and policy compliance management across your infrastructure.

## Use Cases

Compleasy is ideal for:

- **Security Compliance Monitoring**: Ensure servers meet security policies and regulatory requirements
- **Infrastructure Auditing**: Track security posture across multiple servers from a single dashboard
- **Change Tracking**: Monitor changes between audit runs to identify security drift
- **Policy Enforcement**: Automatically evaluate compliance against organizational policies
- **Centralized Reporting**: Single point of visibility for all server audits across your infrastructure

## Features

### Core Capabilities

- **Centralized Audit Collection**: Receives audit reports from multiple Linux servers via Lynis clients, storing full reports and generating diff reports to track changes over time
- **Device Management**: Tracks all monitored servers with metadata including hostname, OS, distribution, version, and compliance status
- **Policy & Compliance Management**: Define custom compliance rules using a query language and automatically evaluate devices against assigned policies
- **Report Analysis**: View complete audit reports, track changes between audits, and analyze historical compliance trends
- **Web Dashboard**: User-friendly interface for viewing devices, compliance status, policies, and reports
- **API Integration**: Lynis-compatible API endpoints for seamless integration with existing Lynis installations


## Security Philosophy

> **We don't compromise the security of the servers we protect.**

Compleasy follows a **read-only security model** to ensure maximum protection for your infrastructure:

- **Read-Only Operations**: Compleasy only **reads** audit data from your servers. It never pushes changes, executes commands, or modifies configurations on monitored servers.
- **Passive Monitoring**: All data flows one-way: from your servers to Compleasy. Your servers remain completely autonomous and secure.
- **Minimal Requirements**: The only requirement on monitored servers is [Lynis](https://cisofy.com/lynis/), a well-established, popular open-source security auditing tool that is:
  - **Well-maintained** by the security community
  - **Easily installable** via standard package managers (`apt`, `yum`, `dnf`, etc.)
  - **Simple to update** through your existing package management workflow
  - **Non-intrusive** - runs audits without modifying system state

This approach ensures that Compleasy enhances your security posture without introducing new attack vectors or dependencies on your production servers.

## Installation vía Docker

### Prerequisites

Before starting, you need to set up the required environment variables:

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Generate a secure SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

3. Edit the `.env` file and replace `GENERATE_THIS_SECRET_KEY_AS_EXPLAINED_ABOVE` with your newly generated key.

4. (Optional) For development environments only, you can enable DEBUG mode by adding `DJANGO_DEBUG=True` to your `.env` file.
5. (Recommended) Set `DJANGO_ALLOWED_HOSTS` to a comma-separated list of your domains in production.
6. (Optional) Enable HTTPS security headers in production:
   - `SECURE_SSL_REDIRECT=True`
   - `SECURE_HSTS_SECONDS=31536000`
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`
7. (Optional) Configure rate limiting:
   - `RATELIMIT_ENABLE=True` (default)
8. (Recommended) PostgreSQL in production (SQLite is used by default):
   - Set `DATABASE_URL=postgresql://user:password@host:5432/dbname`
   - See "PostgreSQL Setup" section below for detailed instructions

> [!CAUTION]
> **Security Critical:** NEVER set `DJANGO_DEBUG=True` in production environments. Running with DEBUG enabled exposes sensitive information including stack traces, environment variables, and database queries to potential attackers. The default is `False` for security.

### Setup

1. Clone the repository:

```bash
git clone https://github.com/compleasy/compleasy.git
```

2. Change to the project directory:

```bash
cd compleasy
```

> [!IMPORTANT]
> **Security Note:** The `SECRET_KEY` is a critical security setting for Django. Never commit your actual secret key to version control. The `.env` file is excluded from git to protect your secrets. For production deployments, always generate a new unique SECRET_KEY.

3. Run docker compose:

```bash
docker compose up
```

## Client configuration

1. Install Lynis:

```bash
sudo apt install lynis
```

2. Generate a Lynis custom profile `/etc/lynis/custom.prf`:

```ini
# Custom profile for Compleasy
upload=yes
# License key will be generated by the server on the first run
license-key=YOUR_LICENSE_KEY
# Point to the Compleasy server
upload-server=yourserver:3000/api/lynis
# Required for self-signed certificates
upload-options=--insecure

# Custom settings
# Too slow. Old systems do not support ignoring some directories
test_skip_always=CRYP-7902
```

3. Run Lynis with the custom profile and upload the results to the Compleasy server:

```bash
lynis audit system --upload --quick
```

> [!NOTE]
> You can use `lynis only-upload` to upload the last audit results.

4. Schedule the audit with a cron job (available in recent Debian/Ubuntu versions):

```bash
systemctl start lynis.timer
```

5. (Recommended) Install the following packages to get the most out of Lynis:

```bash
sudo apt install rkhunter auditd aide
```


## Using Compleasy

1. Access the Compleasy server at `http://yourserver:3000`.

### Collecting Static Files for Production

Before deploying to production, collect static files:

```bash
docker compose -f docker-compose.yml run --rm compleasy python manage.py collectstatic --no-input
```

This collects all static files into `STATIC_ROOT` (default: `staticfiles/`) for serving by Nginx/Apache.

### Advanced configuration

- **Add a license key**: `curl -k https://yourserver:3000/admin/license -X POST -d "licensekey=YOUR_LICENSE`
- **Empty the database**: `curl https://yourserver:3000/admin/db/init?delete=true -k`

## PostgreSQL Setup (Recommended for Production)

Compleasy uses SQLite by default for easy installation, but PostgreSQL is **strongly recommended** for production deployments due to better performance, concurrency, and reliability.

### Why PostgreSQL?

- **Better Performance**: Handles concurrent connections and large datasets more efficiently
- **Concurrency**: SQLite has limitations with concurrent writes
- **Reliability**: Better transaction handling and data integrity
- **Scalability**: Better suited for production workloads

### Quick Setup with Docker Compose

The easiest way to set up PostgreSQL is using Docker Compose. Add a PostgreSQL service to your `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: compleasy
      POSTGRES_USER: compleasy_user
      POSTGRES_PASSWORD: your_secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U compleasy_user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Then set the `DATABASE_URL` environment variable in your Compleasy service:

```yaml
services:
  compleasy:
    environment:
      DATABASE_URL: postgresql://compleasy_user:your_secure_password_here@postgres:5432/compleasy
```

### Manual PostgreSQL Setup

1. **Install PostgreSQL** (if not using Docker):

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql
brew services start postgresql

# Or use your distribution's package manager
```

2. **Create Database and User**:

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE compleasy;
CREATE USER compleasy_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE compleasy_user SET client_encoding TO 'utf8';
ALTER ROLE compleasy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE compleasy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE compleasy TO compleasy_user;
\q
```

3. **Set DATABASE_URL Environment Variable**:

```bash
export DATABASE_URL=postgresql://compleasy_user:your_secure_password_here@localhost:5432/compleasy
```

Or add it to your `.env` file or Docker Compose configuration.

4. **Run Migrations**:

```bash
docker compose exec compleasy python manage.py migrate
```

### Verifying PostgreSQL Connection

After setting up PostgreSQL, verify the connection:

```bash
# Check if Compleasy can connect
docker compose exec compleasy python manage.py dbshell

# Or test the connection
docker compose exec compleasy python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("PostgreSQL connection successful!")
```

### Migration from SQLite to PostgreSQL

If you're already running with SQLite and want to migrate to PostgreSQL:

1. **Backup your SQLite database** (see Backup & Recovery section)
2. **Set up PostgreSQL** (as described above)
3. **Export data from SQLite**:

```bash
# Export data
docker compose exec compleasy python manage.py dumpdata > backup.json
```

4. **Load data into PostgreSQL**:

```bash
# Make sure DATABASE_URL points to PostgreSQL
docker compose exec compleasy python manage.py loaddata backup.json
```

> [!NOTE]
> SQLite is perfectly fine for small deployments, testing, or development. PostgreSQL becomes important when you have multiple concurrent users, large amounts of data, or need high availability.

## Development & Testing

### Prerequisites

- Docker and Docker Compose
- No local Python installation required

### Setup Development Environment

No local installation required! All development and testing happens in Docker containers.

The test container automatically runs database migrations before executing tests.

### Security Notes

- Never use default admin credentials in production. Set `COMPLEASY_ADMIN_PASSWORD` in your `.env`.
- Set `DJANGO_ALLOWED_HOSTS` to your production domains (comma-separated).
- Keep `DJANGO_DEBUG=False` in production.
- When serving over HTTPS, enable HSTS and secure cookies as shown above.

### Running Tests Locally

All tests run inside Docker containers - no local installation required.

#### Unit Tests

Run all unit tests:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test
```

Run specific test file:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py -v
```

Run with HTML coverage report:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest --cov=api --cov=frontend --cov-report=html --cov-report=term-missing
```

Run specific test:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py::TestUploadReport::test_upload_report_valid_license_new_device -v
```

Run tests excluding integration tests:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m "not integration" -v
```

Access the test container shell for debugging:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test /bin/bash
```

#### Integration Tests

Integration tests require Docker and test the full Lynis workflow:

1. Start the development environment:

```bash
# Set environment variables
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
export COMPLEASY_LICENSE_KEY=test-license-key-$(date +%s)

# Start services
docker compose -f docker-compose.dev.yml up -d compleasy
```

2. Wait for the service to be ready:

```bash
# Wait for health check
docker compose -f docker compose.dev.yml ps
```

3. Create a test license key in the database:

```bash
docker compose -f docker compose.dev.yml exec compleasy-dev python manage.py shell <<EOF
from django.contrib.auth.models import User
from api.models import LicenseKey
user = User.objects.first()
LicenseKey.objects.create(licensekey='$COMPLEASY_LICENSE_KEY', created_by=user)
EOF
```

4. Run the Lynis integration test:

```bash
docker compose -f docker-compose.dev.yml up --abort-on-container-exit lynis-client
```

5. Run Python integration tests:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests_integration.py -v -m integration
```

6. Cleanup:

```bash
docker compose -f docker-compose.dev.yml down -v
```

### Project Structure

#### Code Organization

- `src/api/` - API application (models, views, forms, tests)
  - `src/api/utils/` - Utility modules (compliance, lynis_report, policy_query)
- `src/frontend/` - Frontend application (views, templates, static files)
- `src/compleasy/` - Django project settings
  - `src/compleasy/settings/` - Environment-specific settings package
    - `base.py` - Common settings shared across all environments
    - `development.py` - Development-specific settings (default)
    - `production.py` - Production-specific settings
    - `testing.py` - Testing-specific settings
- `src/conftest.py` - Pytest fixtures

#### Settings Configuration

Settings are organized by environment using the `DJANGO_ENV` environment variable:

- **Development** (`DJANGO_ENV=development` or unset): Debug mode enabled, relaxed security
- **Production** (`DJANGO_ENV=production`): Debug disabled, strict security, requires `DJANGO_ALLOWED_HOSTS` (SQLite used by default, PostgreSQL recommended)
- **Testing** (`DJANGO_ENV=testing`): In-memory SQLite, faster password hashing, rate limiting disabled

The settings package automatically loads the appropriate configuration based on `DJANGO_ENV`.

#### API Versioning

Compleasy supports API versioning while maintaining backward compatibility:

- **Versioned API**: `/api/v1/lynis/upload/`, `/api/v1/lynis/license/`
- **Legacy API**: `/api/lynis/upload/`, `/api/lynis/license/` (for Lynis client compatibility)

Both endpoints route to the same views. The legacy endpoints are maintained for external Lynis installations.

### Test Structure

- `src/api/tests.py` - Unit tests for API endpoints (`upload_report`, `check_license`)
- `src/api/tests_integration.py` - Integration tests for end-to-end Lynis workflow
- `src/conftest.py` - Shared pytest fixtures (LicenseKey, Device, mock Lynis reports)
- `pytest.ini` - Pytest configuration
- `docker compose.dev.yml` - Development environment with Compleasy and Lynis client
- `lynis/Dockerfile` - Docker image for Lynis client testing
- `lynis/run-lynis-test.sh` - Script to automate Lynis scan and report upload

### Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

The CI pipeline includes:
- Unit tests with coverage reporting
- Integration tests with Docker
- Code quality checks

See `.github/workflows/test.yml` for the complete CI configuration.

## Acknowledgments

Compleasy is built on [Lynis](https://cisofy.com/lynis/), an excellent open-source security auditing tool. We are grateful to the Lynis project and its community for providing such a robust foundation.

### Important Note

**Compleasy is not a professional product.** This is an open-source project in active development. If you are looking for a robust, production-ready security solution with professional support, service level agreements, and enterprise features, we recommend considering [Lynis Enterprise](https://cisofy.com/pricing/) by CISOfy.

> **Note:** We have no relationship, affiliation, or partnership with CISOfy. This recommendation is made solely to help users find appropriate solutions for their needs.

## License

Compleasy is licensed under the **GNU General Public License v3.0** (GPL-3.0).

See the [LICENSE](LICENSE) file for the full license text.