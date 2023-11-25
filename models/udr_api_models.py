from pydantic import BaseModel, Field, schema, constr
from uuid import UUID, uuid4

class GuamiModel(BaseModel):
    mcc: constr(pattern=r'^[0-9]{3}$')
    mnc: constr(pattern=r'^[0-9]{2,3}$')
    amfId: constr(pattern=r'^[0-9]{2,10}$')

class ItemDataModel(BaseModel):
    amfInstanceId: str
    deregCallbackUri: str
    guami: GuamiModel
    ratType: constr(pattern=r'^(NR|EUTRA|NBIOT|LTE_M|NR_U|VIRTUAL|TRUSTED_N3GA|TRUSTED_WLAN|WIRELINE|WIRELINE_CABLE|WIRELINE_BBF)$')

    @classmethod
    def get_json_schema_example(cls):
        json_schema = schema(cls)
        example = json_schema.get('example', {})
        return example    