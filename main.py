import asyncio
import datetime

import pytz
import requests
import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def return_time(timestamp: int):
    return datetime.datetime.fromtimestamp(timestamp)


update = '02:03'  # Начальное фиксированное время


def write_data():
    database = {}
    global update
    for region in ['americas', 'europe', 'se_asia', 'china']:
        data = requests.get(
            f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={region}&leaderboard=0'
        ).json()
        leaderboard = data.get('leaderboard')

        for idx, player in enumerate(leaderboard, start=1):
            player['rank'] = idx

        database[region] = leaderboard

        database['next_scheduled_post_time'] = data.get('next_scheduled_post_time')
        database['time_posted'] = data.get('time_posted')

        next_update = return_time(data.get('next_scheduled_post_time')).time()

    update = next_update.strftime('%H:%M')

    with open(f'data.json', 'w') as file:
        json.dump(database, file)


async def scheduled_task():
    while True:
        await asyncio.sleep(1)
        now = datetime.datetime.now().time().strftime('%H:%M')
        if now == update:
            write_data()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduled_task())


@app.get("/", response_class=RedirectResponse)
async def default_region():
    return RedirectResponse(url="/europe")


@app.get("/{region}", response_class=HTMLResponse)
async def read_root(request: Request, region: str, rank_from: int | str = None, rank_to: int | str = None,
                    country: str = None,
                    team: str = None,
                    name_player: str = None):
    with open('data.json') as file:
        data = json.load(file)

    leaderboard = data.get(region)

    next_update_time = data.get('next_scheduled_post_time')
    last_update_time = data.get('time_posted')

    if rank_from and rank_to:
        try:
            rank_from = int(rank_from)
            rank_to = int(rank_to)
            leaderboard = leaderboard[rank_from - 1:rank_to]
            # leaderboard = [player for player in leaderboard if rank_from <= player.get('rank') <= rank_to]
        except ValueError:
            pass

    if country:
        leaderboard = [player for player in leaderboard if
                       player.get('country') and country.lower() in player['country'].lower()]

    if team:
        if team == 'yes':
            leaderboard = [player for player in leaderboard if player.get('team_tag')]
        elif team == 'no':
            leaderboard = [player for player in leaderboard if not player.get('team_tag')]

    if name_player:
        leaderboard = [i for i in leaderboard if
                       i.get('name') and i.get('name').lower().startswith(name_player.lower())]

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
            'team': team,
            'name_player': name_player
        }
    )
