# Contributing to Senior Python CRM

Спасибо за интерес к проекту!

## Code Style

- Python 3.10+ with full type hints
- Follow PEP 8 (enforced by ruff)
- Use async/await for all I/O operations
- Type checking with mypy/pyright

## Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`
6. Format code: `make format`
7. Commit with clear messages
8. Push and create a Pull Request

## Testing Requirements

- All new features must have tests
- Maintain or improve code coverage
- Use pytest with async support
- Test edge cases and error handling

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update CHANGELOG if applicable
4. Request review from maintainers

## Questions?

Open an issue for discussion before major changes.
