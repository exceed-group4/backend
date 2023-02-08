from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv('.env')

user = os.getenv('user')
password = os.getenv('password')

client = MongoClient(f"mongodb://{user}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")
db = client['exceed04']
collection = db['miniproject']

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ControlFront(BaseModel):
    id: int
    mode: int # 1 : auto, 2 : manual
    status: int # 0 : false, 1 : true
    light: int

class ControlHard(BaseModel):
    id: int
    status: int # 0 : false, 1 : true

@app.get("/")
def root():
    return {"Hello": "World"}

@app.put("/update/front")
def updateFromFront(control: ControlFront):
    id = control.id
    mode = control.mode
    status = control.status
    light = control.light
    find = collection.find_one({"id": id})
    if(find is None):
        raise HTTPException(400, {"Detail": "Id not found"})
    if((mode!=1 and mode!=2) or type(status)!=int or light>255 or light<0):
        raise HTTPException(400, {"Detail": "Not correct data"})
    collection.update_one({"id": id}, {"$set": control.dict()})
    return {"detail": "Update success"}

@app.get("/status")
def getStatus():
    result = []
    find = collection.find({}, {"_id": 0})
    # print(find)
    for i in find:
        # print(type(i))
        result.append(i)
    return result

@app.put("/update/hard")
def updateFromHard(control: ControlHard):
    id = control.id
    status = control.status
    find = collection.find_one({"id": id})
    if(find is None):
        raise HTTPException(400, {"Detail": "Id not found"})
    if(type(status)!=int):
        raise HTTPException(400, {"Detail": "Not correct data"})
    if find["mode"] == 2 :
        collection.update_one({"id": id}, {"$set": control.dict()})
        return {"detail": "Update success"}
    else :
        raise HTTPException(300, {"Detail": "mode auto"})