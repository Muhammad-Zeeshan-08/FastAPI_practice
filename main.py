from asyncio.windows_events import NULL
from unittest.mock import Base
from pydantic import BaseModel

from fastapi import FastAPI
import uvicorn
from typing import Optional

app = FastAPI()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!      GET Request Practice    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.get("/")
def show():
    return {'data' : 456}

# here i does not make any route for /user only
# When we does not mention any DT, then by default it assumes/is int. for eg here var name is id & its DT not mention
@app.get("/user/{id}")
def show(id):
    return {'data':id}

# Here the route/url is /user, but when func expected some para than we MUST have to pass in url
# /user or /user?MZ etc are WRONG           # /user?name=MZ CORRECT
# @app.get("/user")    
# def show(name):
#     return {'user_name':name}

# Multiple Query Parameter with & w/o default parameter:
# Non-default parameter ko default parameter ke baad nahi rakh sakte +  Or Hamesha Har haal m Non-Default para ki value deni hoti h.
@app.get("/user")    
def show(name, id: int=0):  # def show(name: str=None, id: int=0): WRONG
    return {'user_name':name, 'id':id}

@app.get("/blog")
# def show(limit = 10, published: bool):  Goal: Set limit as default with val 10    Wrong
# 2 Correct Approach: We have to Set Default value for all Parameters or Set them as Optional
# def show(limit = 10, published: bool = True): 
# def show(limit = 10, published: bool = True, sort: Optional[str] = None): 
def show(limit, published: bool): 
    if published:
        return {'data' : "yeah buddy"}
    else:
        return {'data' : "oh no buddy"}

@app.get("/blog/{id}")
def show(id : int):
    return {'data' : id}

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!      POST Request Practice    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Simple post method, and para are mention in function. Benefit: data validation & url is valid. Loss: Limited para 
@app.post("/create-u1")
def user_creation(name:str, age:int):
    return{
        "name" : name,
        "age" : age
    }

# Here entire dic can be passed by the user. Benefit: No para limit, url is valid. Loss: No data validation 
@app.post("/create-u2")
def user_creation(dic: dict):
    return{
        "message" : "User Created",
        "data" : dic
    }

class User(BaseModel):
    name: str
    age: int
@app.post("/create-u3")
def user_creation(user: User):
    return{
        "message" : "User Created",
        "data" : user
    }
# Nested Pydantic
class Address(BaseModel):
    user: User
    city: str
    postal_code: int
@app.post("/create-u4")
def user_creation(comp: Address):
    return{
        "message" : "User Created",
        "data" : comp
    }

# FastAPI Request Parameter Handling: Path + Query + Request Body
# eg; PUT /Person/{id}?notify=true. Path parameter[id] + Query parameter[notify] + Request Body[update_Person]
Person_list = []
class Person(BaseModel):
    name: str
    age: int
@app.post("/Person")
def upload_Person(Person: Person):
    Person_list.append(Person)
    return{
        "message": "Person Created",
        "data": Person
    }
@app.put("/Person/{id}")
def update_Person(id:int, update_Person: Person, notify: bool= False):
    if id< len(Person_list):
        Person_list[id] = update_Person
        return{
            "message": "Person Created",
            "notify": notify,
            "updated_data": update_Person
        }
    return{
        "Error": "That specific Person not found" 
    }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

# @()