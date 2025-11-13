# Compleasy Documentation

This directory contains the MkDocs documentation for Compleasy.

## Quick Start

### Install Dependencies

```bash
pip install -r docs/requirements.txt
```

Or using pipx (recommended):

```bash
pipx install mkdocs-material
pipx inject mkdocs-material mkdocs-awesome-pages-plugin mkdocs-git-revision-date-localized-plugin pymdown-extensions
```

### Serve Locally

```bash
mkdocs serve
```

Documentation will be available at `http://127.0.0.1:8000`

### Build Documentation

```bash
mkdocs build
```

Output will be in the `site/` directory.

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## Documentation Structure

- `index.md` - Home page
- `installation/` - Installation guides
- `configuration/` - Configuration options
- `usage/` - User guides
- `api/` - API reference
- `development/` - Development guides
- `snippets/` - Reusable content snippets

## Editing Documentation

1. Edit markdown files in the `docs/` directory
2. Use `mkdocs serve` to preview changes
3. Commit and push changes
4. Documentation will be automatically updated

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

