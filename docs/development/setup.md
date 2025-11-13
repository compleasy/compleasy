# Development Setup

Set up your development environment for Compleasy.

## Prerequisites

- Docker and Docker Compose
- Git
- (Optional) A code editor

No local Python installation required!

## Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/compleasy/compleasy.git
cd compleasy
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Generate a SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Add to `.env`:

```bash
SECRET_KEY=your-generated-key
DJANGO_DEBUG=True
```

### 3. Start Development Services

```bash
docker compose -f docker-compose.dev.yml up
```

This starts:
- Compleasy development server
- Database
- (Optional) Test services

### 4. Access Development Server

```
http://localhost:3000
```

## Development Workflow

### Running Tests

All tests run in Docker:

```bash
# Run all tests
docker compose -f docker-compose.dev.yml --profile test run --rm test

# Run specific test file
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest api/tests.py -v

# Run with coverage
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest --cov=api --cov-report=html
```

### Accessing Shell

```bash
# Django shell
docker compose -f docker-compose.dev.yml exec compleasy python manage.py shell

# Test container shell
docker compose -f docker-compose.dev.yml --profile test run --rm test /bin/bash
```

### Database Migrations

```bash
# Create migration
docker compose -f docker-compose.dev.yml exec compleasy python manage.py makemigrations

# Apply migrations
docker compose -f docker-compose.dev.yml exec compleasy python manage.py migrate
```

## Code Organization

### Settings

Settings are organized by environment:

- `src/compleasy/settings/base.py` - Common settings
- `src/compleasy/settings/development.py` - Development settings
- `src/compleasy/settings/production.py` - Production settings
- `src/compleasy/settings/testing.py` - Testing settings

### Apps

- `src/api/` - API application (models, views, forms, tests)
- `src/frontend/` - Frontend application (views, templates, static files)

### Utilities

- `src/api/utils/` - Utility modules (compliance, lynis_report, policy_query)
- `src/conftest.py` - Pytest fixtures

## Development Tips

- **Hot Reload** - Django development server auto-reloads on code changes
- **Debug Mode** - Enable `DJANGO_DEBUG=True` for detailed error pages
- **Database** - SQLite is used by default for development
- **Logs** - Check container logs: `docker compose logs compleasy`

## Next Steps

- [Testing Guide](testing.md) - Learn about testing
- [Contributing](contributing.md) - Contribution guidelines

