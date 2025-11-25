# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-11-26

### Added
- Complete async multi-tenant CRM backend
- FastAPI with full type hints and async support
- JWT authentication (access + refresh tokens)
- RBAC with 4 roles (owner, admin, manager, member)
- Organizations and user management
- Contacts CRUD with search and filtering
- Deals management with status/stage tracking
- Tasks with due date validation
- Activity log with automatic tracking
- Analytics endpoints (summary, funnel)
- PostgreSQL with SQLAlchemy async
- Alembic migrations
- Comprehensive test suite
- Docker and Docker Compose setup
- Makefile for dev tasks
- ruff, mypy, pyright linting
- OpenAPI documentation
- Production-ready code structure

### Security
- Bcrypt password hashing
- JWT token authentication
- RBAC authorization
- Input validation with Pydantic
- SQL injection protection
