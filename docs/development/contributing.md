# Contributing

Thank you for your interest in contributing to TrikuSec!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs
- Include steps to reproduce
- Provide environment details
- Include relevant logs

### Suggesting Features

- Open a GitHub Issue with the "enhancement" label
- Describe the use case
- Explain the expected behavior

### Submitting Code

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**
   - Follow code style guidelines
   - Write/update tests
   - Update documentation
4. **Run Tests**
   ```bash
   docker compose -f docker-compose.dev.yml --profile test run --rm test
   ```
5. **Commit Changes**
   - Use clear commit messages
   - Reference issue numbers if applicable
6. **Push and Create Pull Request**

## Code Style

### Python

- Follow PEP 8
- Use type hints where appropriate
- Keep functions focused and small
- Write docstrings for public functions

### Django

- Follow Django best practices
- Use Django's built-in features
- Keep views thin, models fat
- Use forms for validation

### Testing

- Write tests for new features
- Maintain or improve test coverage
- Use descriptive test names
- Keep tests fast and isolated

## Development Guidelines

### Critical API Endpoints

!!! warning "Do Not Break"
    These endpoints must remain unchanged for Lynis compatibility:
    - `/api/lynis/upload/`
    - `/api/lynis/license/`

### Docker Commands

Always use `docker compose` (with space), never `docker-compose` (with hyphen).

### Security

- Never commit secrets
- Review security implications
- Follow security best practices
- Test security features

## Pull Request Process

1. **Ensure Tests Pass** - All tests must pass
2. **Update Documentation** - Update relevant docs
3. **Describe Changes** - Clear description in PR
4. **Reference Issues** - Link to related issues
5. **Wait for Review** - Address review comments

## Code Review

- Be respectful and constructive
- Focus on code, not people
- Explain reasoning
- Be open to feedback

## Questions?

- Open a GitHub Issue
- Check existing documentation
- Review code comments

Thank you for contributing to TrikuSec!

