from fastapi import Depends, Request,FastAPI,HTTPException
# from fastapi.security import OAuth2PasswordBearer
import pymongo
import bson
# import jwt
import os
# from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())
myclient = pymongo.MongoClient(os.environ.get("host"))
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

mydb = myclient["local"]
app = FastAPI()
session = dict()

def authorize():
    if session.get("user") == None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

async def findProduct(id):
    x = mydb['products'].find_one({id: bson.ObjectId(id)})
    return x

@app.get("/addItem")
async def AddItem(request: Request):
    authorize()
    # print("request =",request.json())
    products = mydb['products']
    x = await products.insert_one(await request.json())
    return {"status": "success"}

@app.put("/updateItem/{id}")
async def updateItem(id:str,price:int):
    authorize()
    products = mydb['products']
    if findProduct(id) == None:
        return {"status": "failed"}
    id = bson.ObjectId(id)
    products.update_one({"_id":id},{"$set":{"price":price}})
    return {"status": "success"}

@app.delete("/removeItem/{id}")
async def removeItem(id:str):
    authorize()
    products = mydb['products']
    if findProduct(id) == None:
        return {"status": "failed"}
    id = bson.ObjectId(id)
    products.delete_one({"_id":id})
    return {"status": "success"}

@app.put("/updateCart/{id}")
async def updateCart(id:str,item: str):
    cart = mydb['cart']
    cart.update({'userId': id}, {'$push': {'items': bson.ObjectId(item)}})
    return {"status": "success"}

@app.get("/getItems")
async def AddItem():
    authorize()
    # print("request =",request.json())
    products = mydb['products']
    x = list(products.find())
    for i in range(len(x)):
       d=x[i]
       d['_id'] = str(d['_id'])
       x[i] = d
    # print(x)
    return {"status": "success","products": x}


@app.post("/login/{user}/{password}")
async def Login(request: Request,user:str,password:str):
    # print(os.environ.get)
    users = mydb['users']
    x = users.find_one({"email":user, "password":password})
    if x == None:
        return {"status": "failed"}
    x["_id"] = str(x["_id"])
    # print(x)
    # encoded = jwt.encode(x, os.environ.get("secret_key"), algorithm="RS256")
    session['user'] = x
    return {"status": "success","token":session["user"]}


# @app.get("/items/")
# async def read_items(token: str = Depends(oauth2_scheme)):
#     return {"token": token}