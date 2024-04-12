from typing import Annotated
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from bson.json_util import dumps 
import pymongo
import json

from .utils import *
from models.subscriber_models import *
from models.udr_api_models import *

from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure your TracerProvider with a service name
resource = Resource(attributes={
    SERVICE_NAME: "UDR"
})

# Create a new tracer provider with the specified resource
tracer_provider = TracerProvider(resource=resource)

# Acquire a tracer
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("UDR.tracer")

# Acquire a meter.
meter = metrics.get_meter("UDR.meter")

# Now configure the span processor and exporter as before
#otlp_exporter = OTLPSpanExporter()
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)


router = APIRouter()

@router.post("/")
async def create_subscriber(subscriber: Subscriber):

    with tracer.start_as_current_span("[UDR Subscriber]") as span:                        
        span.set_attribute("subscriber.imsi", str(subscriber.auc.imsi))
        span.set_attribute("subscriber.msisdn", str(subscriber.udm_5g_data.udm_msisdn))
        
        with tracer.start_as_current_span("HTTP2 Request Processing") as span:                        
            span.set_attribute("http.request_payload", str(subscriber.model_dump(mode="json")))
            
        with tracer.start_as_current_span("HTTP2 Response Processing") as span:                
            if subscriber.auc.imsi is None :        
                span.set_attribute("http.response_payload", "IMSI can't be null.")
                raise HTTPException(status_code=422, detail = "IMSI can't be null.")
            
            client, db, collection = open_db()
            if collection.find_one({"auc.imsi": subscriber.auc.imsi }):                
                span.set_attribute("http.response_payload", "IMSI Already exists.")
                close_db(client)
                raise HTTPException(status_code=422, detail = "IMSI Already exists.")
            
            else:
                collection.insert_one(subscriber.model_dump(mode="json"))                       
                span.set_attribute("http.response_payload", "Item created successfully, subscriber: " + str(subscriber.model_dump(mode="json")))                
                close_db(client)     
                return {"message": "Item created successfully", "subscriber": subscriber} 

# UDR api:
# GET authentication-data
@router.get("/v1/subscription-data/imsi-{imsi}/authentication-data/authentication-subscription", response_class=PlainTextResponse)
async def get_authentication_data(imsi, user_agent: Annotated[str | None, Header()] = None):
    with tracer.start_as_current_span("[UDR Subscriber]") as span:                        
        span.set_attribute("subscriber.imsi", str(imsi))        

        with tracer.start_as_current_span("HTTP2 Request Processing") as span:                        
            span.set_attribute("http.request_payload", str(f"IMSI: {imsi}"))

        verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)

        j = db().find_subscriber_one(query = { "auc.imsi": imsi })
        if j:

            with tracer.start_as_current_span("HTTP2 Response Processing") as span:                        
                span.set_attribute("http.request_payload", str({
                        "authenticationMethod": j["udm_5g_data"]["authentication_data"]["authentication_method"],
                        "encPermanentKey": str(j["auc"]["enc_key"]).lower(),
                        "sequenceNumber":	{
                            "sqn": '{:012}'.format(j["auc"]["sqn"])
                        },
                        "authenticationManagementField": j["auc"]["amf"],
                        "encOpcKey": str(j["auc"]["opc_enc_key"]).lower()
                    }))

            return JSONResponse(content = {
                        "authenticationMethod": j["udm_5g_data"]["authentication_data"]["authentication_method"],
                        "encPermanentKey": str(j["auc"]["enc_key"]).lower(),
                        "sequenceNumber":	{
                            "sqn": '{:012}'.format(j["auc"]["sqn"])
                        },
                        "authenticationManagementField": j["auc"]["amf"],
                        "encOpcKey": str(j["auc"]["opc_enc_key"]).lower()
                    }
            )
        else:
            raise HTTPException(status_code=404)

# GET am-data        
@router.get("/v1/subscription-data/imsi-{imsi}/{plmn_id}/provisioned-data/am-data", response_class=PlainTextResponse)
async def get_provisioned_data_am_data(imsi, plmn_id, user_agent: Annotated[str | None, Header()] = None):
    verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)
    j = db().find_subscriber_one(query = { "udm_5g_data.udm_imsi": imsi, 
                                            "udm_5g_data.serving_plmn_id.plmn_id": plmn_id  })
                                            
    if j:
        return JSONResponse(content = {
                    "gpsis": j["udm_5g_data"]["serving_plmn_id"]["provisioned_data"]["access_and_mobility_subscription_data"]["gen_public_subscription_ids"],
                    "subscribedUeAmbr": {
                        "uplink": j["udm_5g_data"]["serving_plmn_id"]["provisioned_data"]["access_and_mobility_subscription_data"]["ue_ambr"]["ue_ambr_up_link"],
                        "downlink": j["udm_5g_data"]["serving_plmn_id"]["provisioned_data"]["access_and_mobility_subscription_data"]["ue_ambr"]["ue_ambr_down_link"]
                    },
                    "nssai": {
                        "defaultSingleNssais": [
                            {
                                "sst": j["udm_5g_data"]["serving_plmn_id"]["provisioned_data"]["access_and_mobility_subscription_data"]["nssai"]["single_nssais"]
                            }
                        ]
                    }
                }
        )
    else:
        raise HTTPException(status_code=404)    

# PUT am-data        
@router.put("/v1/subscription-data/imsi-{imsi}/context-data/amf-3gpp-access", response_class=PlainTextResponse)
    
async def put_gpp_amf_access(imsi: str, item_data: ItemDataModel, user_agent: Annotated[str | None, Header()] = None, status_code = 204):    
    verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)
            
    j = db().update_subscriber_one(query = { "udm_5g_data.udm_imsi": imsi },
                                    filter_path = "udm_5g_data.context_data",
                                    new_value = {
                                                    "amf_id":{
                                                        "amf_id_value": item_data.guami.amfId,
                                                        "plmn_id": f"{item_data.guami.mcc}{item_data.guami.mnc}"
                                                    },
                                                    "rat_type": item_data.ratType,
                                                    "amf_instance_id": item_data.amfInstanceId,
                                                    "dereg_callback_uri": item_data.deregCallbackUri
                                                } 
                                    )

    if j is None:        
        raise HTTPException(status_code=404)


