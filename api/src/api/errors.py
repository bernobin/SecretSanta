from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


async def handle_validation_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request contains invalid data.",
        },
    )


async def handle_integrity_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, IntegrityError)

    return JSONResponse(
        status_code=409,
        content={
            "error": "conflict",
            "message": (
                "The request conflicts with existing database data."
            ),
        },
    )

async def handle_value_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, ValueError)

    message = str(exc)

    if "does not exist" in message:
        code = 404
        error = "not_found"
    else:
        code = 409
        error = "business_rule_violation"

    return JSONResponse(
        status_code=code,
        content={
            "error": error,
            "message": message,
        },
    )