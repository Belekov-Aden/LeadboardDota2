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


@app.get("/", response_class=HTMLResponse)
async def default_region(request: Request, rank_from: int | str = None, rank_to: int | str = None, country: str = None,
                         team: str = None):
    return read_root(request, region='europe', rank_from=rank_from, rank_to=rank_to, country=country, team=team)


@app.get("/{region}", response_class=HTMLResponse)
async def read_root(request: Request, region: str, rank_from: int | str = None, rank_to: int | str = None, country: str = None,
                    team: str = None):
    data: dict = requests.get(
        f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={region}&leaderboard=0').json()
    leaderboard = data.get('leaderboard')

    next_update_time = datetime.datetime.fromtimestamp(data.get('next_scheduled_post_time')).strftime(
        '%d.%m.%Y, %H:%M:%S')
    last_update_time = datetime.datetime.fromtimestamp(data.get('time_posted')).strftime('%d.%m.%Y, %H:%M:%S')

    for rank, i in enumerate(leaderboard, start=1):
        i['rank'] = rank

    if rank_from is not None and rank_to is not None:
        try:
            rank_from = int(rank_from)
            rank_to = int(rank_to)
            leaderboard = [player for player in leaderboard if rank_from <= player.get('rank') <= rank_to]
        except ValueError:
            pass

    if country is not None:
        leaderboard = [player for player in leaderboard if
                       player.get('country') and country.lower() in player['country'].lower()]

    if team is not None:
        if team == 'yes':
            leaderboard = [player for player in leaderboard if player.get('team_tag')]
        elif team == 'no':
            leaderboard = [player for player in leaderboard if not player.get('team_tag')]

    return templates.TemplateResponse(
        request=request, name='main/main.html',
        context={
            'region': region,
            "data": leaderboard,
            'last_update': last_update_time,
            'next_update': next_update_time,
            'rank_from': rank_from,
            'rank_to': rank_to,
            'country': country,
            'team': team
        }
    )
