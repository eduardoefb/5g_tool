#!env/bin/python3

# Refs for custom docs:
# https://fastapi.tiangolo.com/how-to/extending-openapi/#self-hosting-javascript-and-css-for-docs


from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException 
from api.udr import router as udr_router
from api.exceptions import http_exception_handler, validation_exception_handler



from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

# app = FastAPI()
app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Include exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# UDR Create subscriber
app.include_router(udr_router, prefix="/subscriber", tags=["subscriber"])

# UDR nudr-dr functions
app.include_router(udr_router, prefix="/nudr-dr", tags=["nudr-dr"])



