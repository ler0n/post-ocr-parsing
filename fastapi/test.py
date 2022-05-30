from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn

from pydantic import BaseModel, HttpUrl, Field, DirectoryPath

class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemOut(BaseModel):
    name: str
    price: float
    tax: Optional[float] = None


#객체생성
app = FastAPI()
templates = Jinja2Templates(directory="template/")

fake_items_db = [
    {'item_name':'foo'},
    {'itme_name':'bar'},
    {'item_name':'kong'}
]

@app.on_event("startup")
def startup_event():
    print("startup event!")

@app.on_event("shutdown")
def shutdown_event():
    print('shutdown event!')
    with open("log.txt", mode="a") as log:
        log.write("app shutdown!")
# '/' 로 접근하면 return 을 보여줌
@app.get("/")
def read_root():
    return {'hello': 'world'}

@app.get("/users/{user_id}") #path parameter 방식
def get_id(user_id):
    return {'user_id': user_id}

# @app.get("/items/") #query parameter 방식
# def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip: skip + limit]

@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemIn):
    return item

@app.get("/login/")
def get_login_form(request: Request):
    return templates.TemplateResponse("login_form.html", context={'request': request})

@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {'username': username, 'password': password}

# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000)