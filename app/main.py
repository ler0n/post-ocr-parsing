from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional
import uvicorn
import requests
import argparse
from pydantic import BaseModel, HttpUrl, Field, DirectoryPath
import serialization
import model.ruleBase.rule_base as rule


app = FastAPI()
templates = Jinja2Templates(directory="template/")
app.mount("/static", StaticFiles(directory="static"), name="static")


# # Python

# api_url = "http://118.222.179.32:30001/ocr/"
# headers = {"secret": "Boostcamp0001"}
# file_dict = {"file": open("example.png", "rb")}
# response = requests.post(api_url, headers=headers, files=file_dict)
# response.json()


@app.on_event("startup") # 어떤 이미지를 선택했는지 이름을 보여주고, api에 통과시키는 과정을 보여준다
def startup_event():

    print(f"{args.img} parsing starts")

@app.get("/")
def homepage(request: Request, response_class=HTMLResponse):
    result = serialization.main(args.img)
    r = rule.mainfun(result)
    name, email, tel, phone, position = r[2:]
    return templates.TemplateResponse("main.html", context={'request': request, 'image_path': args.img, 'name': name,
                                                            'email': email, 'tel': tel, 'phone': phone,
                                                            'position': position})



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='give image path')
    parser.add_argument('--img', default='static/1.png', help='image path')
    args = parser.parse_args()

    uvicorn.run(app, host="127.0.0.1", port=8000)