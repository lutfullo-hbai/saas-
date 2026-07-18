# Contributing to Disipl

Thank you for considering contributing to Disipl! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend)

### Getting Started

1. Fork and clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker compose up -d` for infrastructure
4. Install dependencies: `pip install -e .`
5. Run migrations: `alembic upgrade head`
6. Start the API: `uvicorn src.presentation.api.app:app --reload`

### Running Tests

```bash
pytest tests/
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

### Code Style

- Use Ruff for linting: `ruff check .`
- Format with Ruff: `ruff format .`
- Type hints required for all functions
- Follow Clean Architecture principles

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(M*):` for new features (M0-M9 milestones)
- `fix(M*):` for bug fixes
- `docs(M*):` for documentation
- `chore(M*):` for maintenance

Where `*` is the milestone number (0-9).

## Architecture

The project follows Clean Architecture (DDD) with Hexagonal Ports & Adapters:

- `src/domain/` - Business logic, entities, use cases
- `src/infrastructure/` - External integrations (DB, Telegram, Redis)
- `src/presentation/` - API controllers, Telegram handlers

## Pull Request Process

1. Create a feature branch from `dev`
2. Make your changes following the guidelines above
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a PR with a clear description
