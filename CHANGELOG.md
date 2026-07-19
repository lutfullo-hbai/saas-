# Changelog

All notable changes to the Disipl project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `ICheckInRepository` interface and `PostgresCheckInRepository` implementation
- `SubscriptionModel` DB model with migration (`002_add_subscriptions`)
- `BetaParticipantModel` and `ReferralModel` DB models with migration (`003_add_beta_referral`)
- Real Payme API integration (`PaymeProvider` with auth, create, check, refund)
- Real Click API integration (`ClickProvider` with auth, create, check, refund)
- `SubscriptionService` with DB persistence and tier management
- `Container` DI container for centralized dependency management
- Weekly insight task now gathers real data from DB per user (not hardcoded)
- Frontend: Plans, TaskTemplates, CheckIn, Progress, Settings pages
- Integration tests: API endpoints (`test_api.py`) and payment providers (`test_payment.py`)
- Payment settings in `.env.example` (Payme/Click merchant_id, secret_key)

### Fixed
- `ProcessCheckInUseCase` no longer imports infrastructure models (Clean Architecture)
- `ILLMProvider` conflict resolved — single interface in `interfaces/llm.py`
- `calculate_score()` called with correct parameter names in ProcessCheckInUseCase
- Test regex pattern for `ScoreEvent.formula_version` validation

### Changed
- `ProcessCheckInUseCase` constructor now takes `checkin_repo` and `template_repo` instead of `AsyncSession`
- `CheckIn` and `ScoreEvent` created via repositories (not direct ORM model instantiation)
- Beta group manager uses DB instead of in-memory storage
- Referral service uses DB instead of in-memory storage
- Weekly insight task generates insights for all active users from real DB data
- Admin panel precision-engine endpoint reads/writes to DB config
- Payment providers (`PaymeProvider`, `ClickProvider`) make real HTTP API calls
- `.env.example` updated with payment configuration variables
- `UserModel` field: `is_admin` added for admin role support
