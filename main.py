import time
import datetime

import requests
import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def default_reqion(request: Request):
    return read_root(request, reqion='europe')


@app.get("/{reqion}", response_class=HTMLResponse)
def read_root(request: Request, reqion: str):
    data: dict = requests.get(
        f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={reqion}&leaderboard=0').json()
    reqion = data.get('leaderboard')
    next_update_time = datetime.datetime.fromtimestamp(data.get('next_scheduled_post_time')).strftime(
        '%d.%m.%Y, %H:%M:%S')
    last_update_time = datetime.datetime.fromtimestamp(data.get('time_posted')).strftime('%d.%m.%Y, %H:%M:%S')
    return templates.TemplateResponse(
        request=request, name='main/main.html',
        context={"reqion": reqion, 'last_update': last_update_time, 'next_update': next_update_time}
    )
