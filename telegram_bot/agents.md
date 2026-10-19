# Secret Santa Telegram Bot — Agent Guidelines

## Project overview

This repository contains a custom Secret Santa API built with FastAPI and a Telegram bot that exposes the API's functionality to Telegram users.

The existing application uses Docker Compose with:

- PostgreSQL 17
- Adminer
- A FastAPI service
- A Telegram bot service

The Telegram bot lives in `telegram_bot/` and is being developed as a separate Python application.

## Development approach

Develop the bot incrementally and deliberately.

- Work in small, independently verifiable steps.
- Avoid implementing multiple architectural layers or features at once.
- Explain the purpose of each change before introducing it.
- Verify each step with relevant tests and type checks before proceeding.
- Do not make assumptions about the existing API contract. Inspect the actual OpenAPI schema and generated client before implementing API integration.
- Prefer simple solutions over unnecessary abstractions.

## Technology choices

- Python 3.13
- `python-telegram-bot` 22.x, using its asynchronous API
- FastAPI's OpenAPI schema as the API contract
- `openapi-python-client` for generating a typed API client
- Pyright for strict static type checking; Pylance should remain free of errors and warnings
- Python's built-in `unittest` framework is available for tests
- Docker Compose for running the services

## Project structure

Use the `src` layout:

```
telegram_bot/
├── pyproject.toml
├── Dockerfile
├── openapi/
│   └── openapi.json
├── src/
│   └── secret_santa_bot/
│       ├── __init__.py
│       └── __main__.py
└── tests/
```

Add modules and subpackages only as the implementation requires them.

The Python package must live under `src/secret_santa_bot/`. The `__main__.py` entry point belongs inside that package, not at the `telegram_bot/` directory root.

The local virtual environment is `telegram_bot/.venv/` and is already covered by `.gitignore`.

## Type safety

Strict typing is a core requirement, not a cleanup task for later.

- Configure Pyright with `typeCheckingMode = "strict"`.
- Annotate function parameters and return types.
- Prefer concrete types, typed dataclasses, and appropriately typed collections.
- Avoid `Any`, unnecessary casts, and `type: ignore` suppressions.
- Keep Pylance and command-line Pyright consistent.
- Run `pyright telegram_bot` after meaningful changes.

The initial project has successfully passed Pyright with zero errors, warnings, or informational diagnostics.

## Testability and dependency injection

Every function should be easy to test without installing mocking libraries.

Prefer explicit dependency injection and ordinary Python objects.

- Application functions should receive their dependencies as parameters.
- Use `typing.Protocol` to define interfaces where components need to depend on an abstraction.
- Use handwritten fake implementations of those interfaces in unit tests.
- Avoid mocking libraries and unnecessary monkey-patching.
- Keep global state and environment access at the application boundary.
- Do not make business logic depend directly on Telegram framework objects, HTTP details, or generated client internals.
- Use integration tests when real HTTP/API behavior needs to be verified.

### Environment configuration

Configuration parsing must receive its environment explicitly.

For example:

```
from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str

def load_settings(environ: Mapping[str, str]) -> Settings:
    token = environ["TELEGRAM_BOT_TOKEN"]

    if not token.strip():
        raise ValueError("TELEGRAM_BOT_TOKEN must not be empty")

    return Settings(telegram_bot_token=token)
```

The production entry point reads `os.environ` and passes it to `load_settings()`.

Tests pass ordinary dictionaries directly. Configuration parsing must not access global environment variables itself.

## API client generation

Use `openapi-python-client` to generate the Telegram bot's API client from the FastAPI OpenAPI schema.

- Store the exported schema at `telegram_bot/openapi/openapi.json`.
- Generate the client from the local schema file, not by relying on the API service being available during the Docker build.
- Pin the generator version and manage generated-client runtime dependencies explicitly.
- Regenerate the client when the API schema changes.
- Inspect the generated package, endpoint signatures, models, and error handling before implementing the adapter.
- Do not guess generated method names, request types, response types, or exception behavior.
- Prefer committing the schema and generated code so local development and Pylance can inspect the generated types.
- Ensure the Docker build uses the client generated from the intended schema.

The generated API client should be isolated behind an adapter that implements the application's own typed interface.

## Architecture direction

Keep the following responsibilities separate as the project grows:

- **Telegram adapter:** Handles Telegram updates, commands, callbacks, keyboards, and message presentation.
- **Application layer:** Implements use cases and coordinates operations through injected interfaces.
- **API adapter:** Translates application operations into generated-client calls and maps API responses and errors into application-level results.
- **Configuration and startup:** Reads environment variables, constructs dependencies, and starts the application.

Application use cases should be testable without Telegram, HTTP requests, Docker, or a running database.

## Docker and Compose

The bot must integrate with the existing Docker Compose setup.

- Keep the bot and FastAPI API as separate services.
- Use `http://api:8000` as the bot's API base URL inside Compose.
- Generate the API client during the bot image build from the checked-in schema.
- Keep build-time generation separate from runtime API communication.
- Do not require a running API container to build the bot image.
- Use appropriate health checks and startup dependencies where supported.
- Handle API unavailability at runtime rather than relying solely on Compose startup ordering.
- Do not hardcode secrets into source code or Docker images.

## Current progress

Completed:

1. Created `telegram_bot/src/secret_santa_bot/` and `telegram_bot/tests/`.
2. Added `telegram_bot/pyproject.toml`.
3. Created and activated the local Python 3.13 virtual environment.
4. Installed the project in editable mode with development dependencies.
5. Configured Pyright strict mode and verified that it passes.
6. Installed `python-telegram-bot` 22.8.
7. Established the environment-injection design for configuration.

Configuration should use the explicit `load_settings(environ)` interface described above.

## Immediate next steps

Continue incrementally:

1. Verify the current configuration implementation and its unit tests.
2. Establish the minimal Telegram application entry point using injected settings.
3. Export and inspect the actual FastAPI OpenAPI schema.
4. Generate and inspect the API client.
5. Design the smallest useful application interface based on actual API operations.
6. Implement one use case, its handwritten fake, and its unit tests.
7. Connect that use case to a Telegram handler.
8. Add Docker integration and automated checks after the vertical slice works.

Do not implement all of these steps at once. Complete and verify each step before continuing.
