# Development

Guide for developers contributing to TrikuSec.

## Development Areas

- **[Setup](setup.md)** - Setting up development environment
- **[Testing](testing.md)** - Running and writing tests
- **[UI/UX Architecture](ui-ux-architecture.md)** - Frontend patterns and best practices
- **[Lynis Report Custom Variables](lynis-report-custom-variables.md)** - Parsing pipeline & derived fields
- **[Contributing](contributing.md)** - Contribution guidelines

## Development Environment

TrikuSec development happens entirely in Docker containers - no local Python installation required.

## Quick Start

1. Clone the repository
2. Set up environment variables
3. Start development services
4. Run tests

## Project Structure

- `src/api/` - API application
- `src/frontend/` - Frontend application
- `src/trikusec/` - Django project settings
- `src/conftest.py` - Pytest fixtures
- `tests/` - Test files

## Development Workflow

1. Create a feature branch
2. Make changes
3. Write/update tests
4. Run tests
5. Submit pull request

## Next Steps

- [Development Setup](setup.md) - Get started with development
- [Testing Guide](testing.md) - Learn about testing
- [UI/UX Architecture](ui-ux-architecture.md) - Understand frontend patterns
- [Contributing](contributing.md) - Contribution guidelines

