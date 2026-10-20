Writing

# Secret Santa Telegram Bot — Agent Guidelines

## Project overview

This repository contains a custom Secret Santa API built with FastAPI and a Telegram bot that exposes the API's functionality to Telegram users.

The existing application uses Docker Compose with:

- PostgreSQL 17
- Adminer
- A FastAPI service
- A Telegram bot service

The Telegram bot lives in `telegram_bot/` and is developed as a separate Python application.

## Development approach

Develop the bot incrementally and deliberately.

- Work in small, independently verifiable steps.
- Avoid implementing multiple architectural layers or features at once.
- Explain the purpose of each change before introducing it.
- Verify each step with relevant tests and type checks before proceeding.
- Do not make assumptions about the API contract. Inspect the checked-in OpenAPI schema and generated client before implementing API integration.
- Prefer simple solutions over unnecessary abstractions, but do not reject an abstraction merely because an earlier implementation proved unsuccessful.
- Treat architectural experiments as learning opportunities. Preserve the underlying goals when revising an approach.
- Do not repeat completed setup work unless a change makes it necessary.
- Keep project documentation synchronized with the actual repository state.

## Technology choices

- Python 3.13
- `python-telegram-bot` 22.8, using its asynchronous API
- FastAPI's OpenAPI schema as the API contract
- `openapi-python-client` 0.29.1 for generating the typed API client
- Pyright in strict mode; Pylance should remain free of errors and warnings in application code
- Python's built-in `unittest` framework for tests
- Docker Compose for running the services
- `httpx` and `attrs` as generated-client runtime dependencies

Pin tool versions and manage runtime dependencies explicitly. When changing versions, verify compatibility with the generated client and the project's Python version.

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
│       ├── __main__.py
│       └── generated_client/
│           ├── pyproject.toml
│           └── secret_santa_api_client/
└── tests/
```

This is the current structural outline, not a requirement to create every module in advance. Add modules and subpackages only as implementation requires them.

The Python application package must live under `src/secret_santa_bot/`. The `__main__.py` entry point belongs inside that package, not at the `telegram_bot/` directory root.

The generated API client is located at:

`telegram_bot/src/secret_santa_bot/generated_client/secret_santa_api_client/`

The local virtual environment is `telegram_bot/.venv/` and is covered by `.gitignore`.

Do not add generated caches such as `.ruff_cache` to source control.

## Type safety

Strict typing is a core requirement, not a cleanup task for later.

- Configure Pyright with `typeCheckingMode = "strict"`.
- Annotate function parameters and return types.
- Prefer concrete types, typed dataclasses, and appropriately typed collections.
- Avoid `Any`, unnecessary casts, and `type: ignore` suppressions in application code.
- Keep Pylance and command-line Pyright consistent.
- Run `pyright .` from `telegram_bot/` after meaningful changes.
- Keep generated code out of strict application-code analysis when its generator output produces unrelated diagnostics. Do not weaken strict checking for application code to accommodate generated code.

The generated client initially produced strict Pyright diagnostics concerning unknown collection element types, dictionary types, and additional properties. These were addressed through the project's type-checking configuration rather than manual edits to generated files.

The current baseline passes Pyright with zero errors, warnings, or informational diagnostics.

## Testability and dependency injection

Every function and component should be designed so its behavior can be verified without depending unnecessarily on external frameworks, services, or mocking libraries.

Prefer explicit dependency injection and ordinary Python objects.

- Application functions should receive their dependencies as parameters.
- Use `typing.Protocol` to define interfaces where components need to depend on an abstraction.
- Write handwritten fake implementations of those interfaces for unit tests.
- Do not import mocking libraries such as `unittest.mock`, use automatically generated mocks, or rely on magic mocking frameworks. Test doubles should be explicit Python code that we own and understand.
- Avoid unnecessary monkey-patching and hidden global state.
- Keep environment access at the application boundary.
- Test meaningful behavior through observable outcomes rather than implementation details.
- Use integration tests when real HTTP/API behavior needs to be verified.
- Test successful operations, expected application-level failures, and resource cleanup where relevant.
- Prefer dependency injection over complicated test setup that attempts to intercept framework internals.

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

Keep API configuration, including the API base URL, explicit as the integration is introduced. Validate required settings at startup and never log secrets.

### Testing framework boundaries

The Telegram framework is an external adapter, not the application itself. Its types and lifecycle should not spread unnecessarily into application logic.

The objective is a clear, testable boundary between our application and `python-telegram-bot`, while still allowing the framework to manage the Telegram-specific behavior it is responsible for.

- Keep Telegram update objects, handlers, application objects, and framework-specific types inside the Telegram adapter wherever practical.
- Let the application layer depend on application-owned interfaces and types rather than Telegram framework objects.
- Make the construction and execution of the Telegram adapter independently testable.
- Use explicit dependencies and handwritten fakes to test application behavior without running a Telegram bot or connecting to Telegram.
- When framework behavior itself needs verification, use an appropriate integration test rather than assuming a unit test proves that the real framework behaves correctly.
- Keep strict type checking enabled at the framework boundary. If the framework's generic types or annotations require a suppression, scope it narrowly to the specific boundary expression and document why it is necessary.
- Explore alternative boundary designs when the current design makes dependencies difficult to see, behavior difficult to test, or framework types difficult to contain.

Dependency injection, adapter interfaces, factories, and lifecycle hooks are possible design tools. Choose between them based on the behavior we need to test and the clarity of the resulting application code, not by committing prematurely to one pattern.

## API client generation

Use `openapi-python-client` to generate the Telegram bot's API client from the FastAPI OpenAPI schema.

- Store the exported schema at `telegram_bot/openapi/openapi.json`.
- Generate the client from the checked-in schema file, not by relying on the API service being available during the Docker build.
- Pin the generator version and manage generated-client runtime dependencies explicitly.
- Regenerate the client whenever the API schema changes.
- Inspect generated endpoint signatures, request and response models, and error handling before implementing the adapter.
- Do not guess generated method names, request types, response types, or exception behavior.
- Commit the schema and generated code so local development, code review, and Pylance can inspect the contract.
- Ensure the Docker build uses the client generated from the intended schema.
- Do not manually modify generated files to implement application behavior.
- Keep generation reproducible and verify generated changes when the schema changes.

The exported schema currently identifies the API as **Secret Santa API**, OpenAPI **3.1.0**, version **1.0.0**.

The API base URL is environment-dependent:

- Local development: `http://localhost:8000`
- Docker Compose: `http://api:8000`

The OpenAPI document is stored locally and should be regenerated from the running API when the API contract changes.

### Generated-client dependency management

The generated client is under `src/secret_santa_bot/generated_client/` and contains its own generated `pyproject.toml`.

Treat the generated package metadata as an input to dependency management, not as the bot application's sole dependency specification.

- Keep the bot's install and runtime dependencies explicitly declared in the main project configuration.
- Verify that the generated client's imports resolve in the bot's development and Docker environments.
- Keep compatible `httpx` and `attrs` versions installed.
- Run `python -m pip check` after dependency changes.
- Avoid relying on undeclared transitive dependencies or on the current working directory to make imports succeed.

## Architecture direction

Keep the following responsibilities separate as the project grows:

- **Telegram adapter:** Handles Telegram updates, commands, callbacks, keyboards, message presentation, and framework-specific startup and shutdown.
- **Application layer:** Implements use cases and coordinates operations through injected interfaces.
- **API adapter:** Translates application operations into generated-client calls and maps API responses and errors into application-level results.
- **Configuration and startup:** Reads environment variables, constructs dependencies, and starts the application.

Application use cases should be testable without Telegram, HTTP requests, Docker, or a running database.

The application should make its dependencies explicit. For example, constructing the API client in the composition root and passing it to the Telegram adapter makes that dependency visible and replaceable.

The framework boundary deserves the same attention. The application should be able to control when the adapter is constructed and started, and how resources are cleaned up, without requiring application logic to understand Telegram framework internals.

Explore the smallest design that achieves these goals. Do not introduce abstractions without a concrete use case, but do not confuse avoiding unnecessary abstraction with avoiding useful architectural boundaries.

### API integration principles

- Centralize API client configuration.
- Use the generated client's asynchronous operations in the asynchronous bot application.
- Use the generated client's actual response types and status handling.
- Distinguish API validation failures, unexpected HTTP statuses, timeouts, and connectivity errors where relevant.
- Convert transport and generated-client details into understandable application-level outcomes.
- Avoid exposing internal exception details or sensitive API responses to Telegram users.
- Never assume an operation is idempotent unless the API contract or implementation establishes that behavior.
- Do not automatically retry operations that may create or mutate data without considering duplicate side effects.
- Close asynchronous HTTP resources during application shutdown. Ensure cleanup also occurs when startup or execution fails, according to the resource's ownership and lifecycle.

## Docker and Compose

The bot must integrate with the existing Docker Compose setup.

- Keep the bot and FastAPI API as separate services.
- Use `http://api:8000` as the bot's API base URL inside Compose.
- Generate the API client during the bot image build from the checked-in schema, or package the already generated client in a way that guarantees it corresponds to that schema.
- Keep build-time generation separate from runtime API communication.
- Do not require a running API container to build the bot image.
- Use appropriate health checks and startup dependencies where supported.
- Handle API unavailability at runtime rather than relying solely on Compose startup ordering.
- Do not hardcode secrets into source code or Docker images.
- Ensure `.venv`, caches, and other development artifacts are excluded from Docker build contexts.
- Verify the actual Compose configuration before changing service names, health checks, or dependencies.

## Current progress

Completed:

1. Created `telegram_bot/src/secret_santa_bot/` and `telegram_bot/tests/`.
2. Added `telegram_bot/pyproject.toml`.
3. Created and activated the local Python 3.13 virtual environment.
4. Installed the project in editable mode with development dependencies.
5. Configured Pyright strict mode and verified that it passes.
6. Installed `python-telegram-bot` 22.8.
7. Established the environment-injection design for configuration.
8. Added and verified configuration tests covering valid tokens, missing tokens, empty tokens, and whitespace-only tokens.
9. Exported the FastAPI OpenAPI document to `telegram_bot/openapi/openapi.json`.
10. Verified the schema metadata: OpenAPI 3.1.0, title `Secret Santa API`, version `1.0.0`.
11. Generated the typed API client with `openapi-python-client` 0.29.1.
12. Inspected representative generated endpoint implementations, models, client configuration, and error handling.
13. Configured strict type checking to avoid unrelated diagnostics in generated code without relaxing application-code checks.
14. Removed generated Ruff cache artifacts.
15. Implemented explicit API client construction through `create_api_client(settings)`, including an asynchronous HTTP client configured with the supplied API base URL.
16. Added an API client construction test.
17. Introduced a Telegram adapter that receives the Telegram token and API client explicitly and builds the framework application.
18. Kept Telegram framework generic types within the adapter and resolved the resulting strict Pyright diagnostics.
19. Explored a lifecycle abstraction for Telegram application creation, execution, and cleanup. The experiment was rolled back because it did not make framework injection sufficiently clear in the composition root. The architectural goal of a clean, testable framework boundary remains open for future work.
20. Verified the current baseline:
    - `pyright .`: zero errors, warnings, or informational diagnostics.
    - `python -m unittest discover -s tests -v`: 9 tests pass.
    - `python -m pip check`: no broken requirements.

Run these commands from `telegram_bot/`:

```
pyright .
python -m unittest discover -s tests -v
python -m pip check
```

The current tests cover configuration, API client construction, and API base URL configuration. Telegram runtime behavior and the final framework boundary have not yet been established by dedicated tests.

## Immediate next steps

Proceed one verified step at a time. Do not implement the whole bot at once.

1. **Review the current application entry point and configuration.** Confirm that `load_settings(environ)` is implemented and tested, and identify what is still missing for startup.
2. **Review the current Telegram adapter.** Identify which responsibilities still depend directly on `python-telegram-bot` and which can be expressed through application-owned interfaces.
3. **Explore a testable Telegram boundary.** Define a concrete behavior that should be testable, choose the smallest suitable interface, and demonstrate that a handwritten fake can verify it without running the Telegram framework or connecting to Telegram.
4. **Keep dependency construction explicit.** Ensure that `main()` clearly shows where settings, the API client, and the Telegram adapter are constructed and how they are connected.
5. **Introduce the smallest useful API adapter interface.** Use the generated client's actual types and asynchronous methods. Keep the adapter small and application-specific.
6. **Implement user registration as the first vertical slice.** Inspect the actual create-user and user-retrieval endpoint behavior before deciding how Telegram users map to API users.
7. **Write unit tests using handwritten fakes.** Verify registration and error handling without Telegram, HTTP requests, or a running API.
8. **Connect the use case to one Telegram handler.** Keep Telegram-specific concerns out of the application logic.
9. **Verify the vertical slice.** Run tests, strict Pyright, and dependency checks before proceeding to session management.
10. **Add Docker integration and broader automated checks** after the first vertical slice works.

Do not repeat schema export or client generation unless the contract changes or a reproducibility check requires it. Do not implement session commands, participant management, assignment display, and administration all in the same step.

## Working agreement

Before each implementation step:

1. State the specific goal and why it is needed.
2. Identify the files that need to change.
3. Make the smallest useful change.
4. Add or update tests.
5. Run the relevant checks and report their results.
6. Explain any remaining limitations before moving on.

Never claim that a test, type check, Docker build, or integration test passed unless it was actually run and its result was observed.
