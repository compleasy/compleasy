# PostgreSQL Setup

Compleasy uses SQLite by default for easy installation, but PostgreSQL is **strongly recommended** for production deployments.

## Why PostgreSQL?

- **Better Performance**: Handles concurrent connections and large datasets more efficiently
- **Concurrency**: SQLite has limitations with concurrent writes
- **Reliability**: Better transaction handling and data integrity
- **Scalability**: Better suited for production workloads

## Quick Setup with Docker Compose

The easiest way to set up PostgreSQL is using Docker Compose.

### 1. Add PostgreSQL Service

Add a PostgreSQL service to your `docker-compose.yml`:

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

### 2. Configure DATABASE_URL

Set the `DATABASE_URL` environment variable in your Compleasy service:

```yaml
services:
  compleasy:
    environment:
      DATABASE_URL: postgresql://compleasy_user:your_secure_password_here@postgres:5432/compleasy
```

Or add it to your `.env` file:

```bash
DATABASE_URL=postgresql://compleasy_user:your_secure_password_here@postgres:5432/compleasy
```

### 3. Run Migrations

```bash
docker compose exec compleasy python manage.py migrate
```

## Manual PostgreSQL Setup

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql
brew services start postgresql
```

### 2. Create Database and User

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

### 3. Set DATABASE_URL

```bash
export DATABASE_URL=postgresql://compleasy_user:your_secure_password_here@localhost:5432/compleasy
```

Or add it to your `.env` file.

## Verifying Connection

After setting up PostgreSQL, verify the connection:

```bash
# Check if Compleasy can connect
docker compose exec compleasy python manage.py dbshell

# Or test the connection
docker compose exec compleasy python manage.py shell
```

```python
from django.db import connection
connection.ensure_connection()
print("PostgreSQL connection successful!")
```

## Migration from SQLite

If you're already running with SQLite and want to migrate to PostgreSQL:

1. **Backup your SQLite database**:
   ```bash
   docker compose exec compleasy python manage.py dumpdata > backup.json
   ```

2. **Set up PostgreSQL** (as described above)

3. **Load data into PostgreSQL**:
   ```bash
   docker compose exec compleasy python manage.py loaddata backup.json
   ```

!!! note "SQLite for Development"
    SQLite is perfectly fine for small deployments, testing, or development. PostgreSQL becomes important when you have multiple concurrent users, large amounts of data, or need high availability.

