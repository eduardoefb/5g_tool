#!env/bin/python3

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException 
#from models.subscriber_models import Subscriber, authentication_data, slice, auc
from api.udr import router as udr_router
from api.exceptions import http_exception_handler, validation_exception_handler

app = FastAPI()

# Include exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# UDR Create subscriber
app.include_router(udr_router, prefix="/subscriber", tags=["subscriber"])

# UDR nudr-dr functions
app.include_router(udr_router, prefix="/nudr-dr", tags=["nudr-dr"])

