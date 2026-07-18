# Changelog

All notable changes to the Disipl project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- DB Session dependency for async PostgreSQL connections
- All API endpoints now use real DB sessions
- Admin router with auth-protected endpoints
- Telegram bot full DB integration (goal creation, check-in, progress)
- Scheduler stubs replaced with real async DB queries
- Prometheus metrics instrumentation
- Multi-stage Dockerfile with non-root user
- .dockerignore for smaller Docker images

### Fixed
- Onboarding handler syntax error (text= parameter)
- Frontend login page matches backend response format
- CORS restricted to known origins only
- Task template ownership check (user_id validation)
- Insights endpoint uses real DB queries with proper 403 check

### Changed
- Frontend pages rewritten to use real API calls instead of mocks
- Admin endpoints require authentication
- Telegram routers properly wired in handlers/__init__.py and main.py
