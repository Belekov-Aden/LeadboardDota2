import requests
import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/#{reqion}", response_class=HTMLResponse)
def read_root(request: Request, reqion: str = 'europe'):
    data: dict = requests.get(
        f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={reqion}&leaderboard=0').json()

    reqion = data.get('leaderboard')[0]
    return templates.TemplateResponse(
        request=request, name='main/main.html', context={"reqion": reqion}
    )
