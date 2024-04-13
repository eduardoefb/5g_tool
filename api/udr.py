from typing import Annotated
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from bson.json_util import dumps 
import pymongo
import json
from .utils import *
from .opentelemetry import *
from models.subscriber_models import *
from models.udr_api_models import *

tracer = setup_tracer("UDR")

router = APIRouter()

@router.post("/")
async def create_subscriber(request: Request = None, subscriber: Subscriber = None):
    with start_span(tracer, "Create Subscriber") as span: 
        span.set_attribute("subscriber.imsi", str(subscriber.auc.imsi))
        span.set_attribute("subscriber.msisdn", str(subscriber.udm_5g_data.udm_msisdn))
        span.set_attribute("request.type", str(dict(request)["type"]))
        span.set_attribute("request.http_version", str(dict(request)["http_version"]))
        span.set_attribute("request.method", str(dict(request)["method"]))
        span.set_attribute("request.scheme", str(dict(request)["scheme"]))
        span.set_attribute("request.path", str(dict(request)["path"]))
        span.set_attribute("request.headers", str(dict(request)["headers"]))


        with start_span(tracer, "Create Subscriber Request") as span:                       
            span.set_attribute("subscriber.data.request", str(subscriber.model_dump(mode="json")))
            
        with start_span(tracer, "Create Subscriber Response") as span:          
            if subscriber.auc.imsi is None :        
                span.set_attribute("subscriber.data.response.text", "IMSI can't be null.")
                span.set_attribute("subscriber.data.response.code", "422")
                raise HTTPException(status_code=422, detail = "IMSI can't be null.")
            
            with managed_db_connection() as collection:
                if collection.find_one({"auc.imsi": subscriber.auc.imsi }):                
                    span.set_attribute("subscriber.data.response.text", "IMSI Already exists.")
                    span.set_attribute("subscriber.data.response.code", "422")
                    raise HTTPException(status_code=422, detail = "IMSI Already exists.")
                
                else:
                    collection.insert_one(subscriber.model_dump(mode="json"))                       
                    span.set_attribute("subscriber.data.response.text", "Item created successfully, subscriber: " + str(subscriber.model_dump(mode="json")))                
                    span.set_attribute("subscriber.data.response.code", "200")
                    return {"message": "Item created successfully", "subscriber": subscriber} 

# UDR api:
# GET authentication-data
@router.get("/v1/subscription-data/imsi-{imsi}/authentication-data/authentication-subscription", response_class=PlainTextResponse)
async def get_authentication_data(imsi, user_agent: Annotated[str | None, Header()] = None, request: Request = None):    
    with start_span(tracer, "Get authentication-data") as span:                                
        span.set_attribute("subscriber.imsi", str(imsi))        
        span.set_attribute("request.type", str(dict(request)["type"]))
        span.set_attribute("request.http_version", str(dict(request)["http_version"]))
        span.set_attribute("request.method", str(dict(request)["method"]))
        span.set_attribute("request.scheme", str(dict(request)["scheme"]))
        span.set_attribute("request.path", str(dict(request)["path"]))
        span.set_attribute("request.headers", str(dict(request)["headers"]))             

        with start_span(tracer, "Get authentication-data Request") as span:                                     
            span.set_attribute("subscriber.data.request", str(f"IMSI: {imsi}"))

        verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)

        j = db().find_subscriber_one(query = { "auc.imsi": imsi })
        if j:

            response = {
                        "authenticationMethod": j["udm_5g_data"]["authentication_data"]["authentication_method"],
                        "encPermanentKey": str(j["auc"]["enc_key"]).lower(),
                        "sequenceNumber":	{
                            "sqn": '{:012}'.format(j["auc"]["sqn"])
                        },
                        "authenticationManagementField": j["auc"]["amf"],
                        "encOpcKey": str(j["auc"]["opc_enc_key"]).lower()
                    }

            with start_span(tracer, "Get authentication-data Response") as span:                        
                span.set_attribute("subscriber.data.response.text", str(response))
                span.set_attribute("subscriber.data.response.code", "200")

            return JSONResponse(response)
        else:
            raise HTTPException(status_code=404)

# GET am-data        
@router.get("/v1/subscription-data/imsi-{imsi}/{plmn_id}/provisioned-data/am-data", response_class=PlainTextResponse)
async def get_provisioned_data_am_data(imsi, plmn_id, user_agent: Annotated[str | None, Header()] = None, request: Request = None):
    with start_span(tracer, "Get am-data") as span:                                
        span.set_attribute("subscriber.imsi", str(imsi))        
        span.set_attribute("request.type", str(dict(request)["type"]))
        span.set_attribute("request.http_version", str(dict(request)["http_version"]))
        span.set_attribute("request.method", str(dict(request)["method"]))
        span.set_attribute("request.scheme", str(dict(request)["scheme"]))
        span.set_attribute("request.path", str(dict(request)["path"]))
        span.set_attribute("request.headers", str(dict(request)["headers"]))  
              
        with start_span(tracer, "Get am-data Request") as span:               
            span.set_attribute("subscriber.data.request", str(f"IMSI: {imsi}"))

        verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)    
        j = db().find_subscriber_one(query = { "udm_5g_data.udm_imsi": imsi, 
                                                "udm_5g_data.serving_plmn_id.plmn_id": plmn_id  })
                                    
        if j:
            response = {
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

            with start_span(tracer, "Get am-data Response") as span:                        
                span.set_attribute("subscriber.data.response.text", str(response))
                span.set_attribute("subscriber.data.response.code", "200")

            return JSONResponse(content = response)
        else:
            raise HTTPException(status_code=404)    

# PUT am-data        
@router.put("/v1/subscription-data/imsi-{imsi}/context-data/amf-3gpp-access", response_class=PlainTextResponse)
    
async def put_gpp_amf_access(imsi: str, item_data: ItemDataModel, user_agent: Annotated[str | None, Header()] = None, status_code = 204, request: Request = None):    

    with start_span(tracer, "Put am-data") as span:                                
        span.set_attribute("subscriber.imsi", str(imsi))        
        span.set_attribute("request.type", str(dict(request)["type"]))
        span.set_attribute("request.http_version", str(dict(request)["http_version"]))
        span.set_attribute("request.method", str(dict(request)["method"]))
        span.set_attribute("request.scheme", str(dict(request)["scheme"]))
        span.set_attribute("request.path", str(dict(request)["path"]))
        span.set_attribute("request.headers", str(dict(request)["headers"]))  

        with start_span(tracer, "Put am-data Request") as span:     
            verify_user_agent(allowed_user_agents = ["UDM"], user_agent = user_agent)
            input_data =  {
                                "amf_id":{
                                    "amf_id_value": item_data.guami.amfId,
                                    "plmn_id": f"{item_data.guami.mcc}{item_data.guami.mnc}"
                                },
                                "rat_type": item_data.ratType,
                                "amf_instance_id": item_data.amfInstanceId,
                                "dereg_callback_uri": item_data.deregCallbackUri
                            }
            span.set_attribute("subscriber.data.request", str(f"IMSI: {imsi}"))
            span.set_attribute("subscriber.data.input_data", str(dict(input_data)))


            with start_span(tracer, "Put am-data Response") as span:                     
                j = db().update_subscriber_one(query = { "udm_5g_data.udm_imsi": imsi },
                                                filter_path = "udm_5g_data.context_data",
                                                new_value = input_data
                                                )

                span.set_attribute("subscriber.data.response.text", str(j))                
                if j is None:        
                    raise HTTPException(status_code=404)
                    span.set_attribute("subscriber.data.response.code", "404")
                else:
                    span.set_attribute("subscriber.data.response.code", "200")


