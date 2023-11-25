from fastapi import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)
