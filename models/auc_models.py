from pydantic import BaseModel, Field, schema, constr
from uuid import UUID, uuid4

class auc(BaseModel):
    imsi: constr(pattern=r'^[0-9]{15}$')
    enc_key: constr(pattern=r'^[A-F0-9]{32}$')
    opc_enc_key: constr(pattern=r'^[A-F0-9]{32}$')
    amf: int = 8000
    sqn: int = 0