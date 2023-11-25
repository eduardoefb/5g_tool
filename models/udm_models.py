from pydantic import BaseModel, Field, schema, constr
from uuid import UUID, uuid4

# Data definition:
class authentication_data(BaseModel):
    authentication_method: constr(pattern=r'^(5G_AKA|EAP_AKA|EAP_TLS)$') 

class nssai(BaseModel):
    single_nssais: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {    
                    "single_nssais": "171-121234"                
                }
            ]
        }
    }    

class ue_ambr(BaseModel):
    ue_ambr_up_link: str
    ue_ambr_down_link: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {    
                    "ue_ambr_up_link": "10 Tbps",
                    "ue_ambr_down_link": "1 Tbps"               
                }
            ]
        }
    }      

class access_and_mobility_subscription_data(BaseModel):
    nssai: nssai
    ue_ambr: ue_ambr
    gen_public_subscription_ids: list[constr(pattern=r'msisdn-[0-9]{10,15}')]

class provisioned_data(BaseModel):
    access_and_mobility_subscription_data: access_and_mobility_subscription_data

class serving_plmn_id(BaseModel):
    plmn_id: str
    provisioned_data: provisioned_data

class udm_amf_3gpp_guami(BaseModel):
    amf_id_value: constr(pattern=r'^[0-9]{6}$')
    plmn_id: constr(pattern=r'^[0-9]{5,6}$')

class amf3gpp_access_registration(BaseModel):
    amf_id: udm_amf_3gpp_guami
    amf_instance_id: str    
    rat_type: constr(pattern=r'^(NR|EUTRA|NBIOT|LTE_M|NR_U|VIRTUAL|TRUSTED_N3GA|TRUSTED_WLAN|WIRELINE|WIRELINE_CABLE|WIRELINE_BBF)$')
    dereg_callback_uri: str

class context_data(BaseModel):
    amf3gpp_access_registration: amf3gpp_access_registration

class udm_5g_data(BaseModel):
    authentication_data: authentication_data
    serving_plmn_id: serving_plmn_id    
    context_data: context_data = None
    udm_imsi: constr(pattern=r'^[0-9]{15}$')
    udm_msisdn: constr(pattern=r'^[0-9]{1,15}$') = None
