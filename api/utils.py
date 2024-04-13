import os
import pymongo
from fastapi import APIRouter, HTTPException, Header
from bson.json_util import dumps
import json
from jsonpath_ng import jsonpath, parse
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.trace import StatusCode

mongo_db_name = os.environ.get("DATABASE_NAME")
mongo_db_user = os.environ.get("DATABASE_USER")
mongo_db_pass = os.environ.get("DATABASE_PASS")
mongo_external_ip = os.environ.get("MONGODB_EXTERNAL_IP")
subscriber_collection_name = os.environ.get("SUBSCRIBER_COLLECTION_NAME")
mongo_url = f"mongodb://{mongo_db_user}:{mongo_db_pass}@{mongo_external_ip}"

def open_db():
    client = pymongo.MongoClient(mongo_url)
    db = client[mongo_db_name]
    collection = db[subscriber_collection_name]  
    return client, db, collection 

def close_db(client):
    client.close()

def verify_user_agent(allowed_user_agents, user_agent):    
    if not user_agent:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid User Agent")
    elif not user_agent in allowed_user_agents:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid User Agent")    

class db:
    def __init__(self):
        self.__mongo_db_name = os.environ.get("DATABASE_NAME")
        self.__mongo_db_user = os.environ.get("DATABASE_USER")
        self.__mongo_db_pass = os.environ.get("DATABASE_PASS")
        self.__mongo_external_ip = os.environ.get("MONGODB_EXTERNAL_IP")
        self.__subscriber_collection_name = os.environ.get("SUBSCRIBER_COLLECTION_NAME")        
        self.__client = pymongo.MongoClient(mongo_url)
        self.__db = self.__client[mongo_db_name]
        self.__subscriber_collection = self.__db[subscriber_collection_name]
    
    def close(self):
        self.__client.close()

    def find_subscriber_one(self, query):
        out = None
        res = self.__subscriber_collection.find_one(query)
        if res:
            p = dumps(res)
            out = json.loads(p)
        self.close()
        return out

    def update_subscriber_one(self, query, filter_path, new_value):
        out = None
        res = self.__subscriber_collection.find_one(query) 
        
        if res:
            parse(filter_path).update(res, new_value)            
            self.__subscriber_collection.update_one({'_id': res['_id']}, {'$set': res})
            out = 0
        self.close()
        return out        

from contextlib import contextmanager

@contextmanager
def managed_db_connection():
    client, db, collection = open_db()
    try:
        yield collection
    finally:
        close_db(client)

@contextmanager
def start_span(tracer, name):
    with tracer.start_as_current_span(name) as span:        
        try:            
            yield span       
        except Exception as e:
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, str(e))
            raise        