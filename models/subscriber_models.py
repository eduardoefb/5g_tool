from pydantic import BaseModel, Field, schema, constr
from uuid import UUID, uuid4

# Import models from AUC:
from models.auc_models import *
from models.udm_models import *

class Subscriber(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    auc: auc
    udm_5g_data: udm_5g_data    
        
    @classmethod
    def get_json_schema_example(cls):
        json_schema = schema(cls)
        example = json_schema.get('example', {})
        return example
