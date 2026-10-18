from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from src.api.routes import sessions
from src.classes.database import Database
from src.api.errors import (
    handle_integrity_error,
    handle_validation_error,
    handle_value_error,
)
from src.api.routes import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = Database(os.environ["DATABASE_URL"])
    app.state.database = database

    try:
        yield
    finally:
        await database.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Secret Santa API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(users.router)
    app.include_router(sessions.router)

    app.add_exception_handler(
        RequestValidationError,
        handle_validation_error,
    )
    app.add_exception_handler(
        IntegrityError,
        handle_integrity_error,
    )

    app.add_exception_handler(ValueError, handle_value_error)

    return app


app = create_app()
