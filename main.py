import asyncio
import datetime
from collections import defaultdict

import pytz
import requests
import json
from iso3166 import countries_by_alpha2

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def write_data():
    database = {}
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

    with open(f'data.json', 'w') as file:
        json.dump(database, file)


async def scheduled_task():
    while True:
        write_data()
        await asyncio.sleep(3600)  # Обновление каждые 60 минут (3600 секунд)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduled_task())


@app.get("/", response_class=RedirectResponse)
async def default_region():
    return RedirectResponse(url="/europe")


@app.get("/{region}", response_class=HTMLResponse)
async def read_root(request: Request, region: str, rank_from: int | str = None, rank_to: int | str = None,
                    countries: str = None,
                    team: str = None,
                    name_player: str = None):
    with open('data.json') as file:
        data = json.load(file)

    leaderboard = data.get(region)

    next_update_time = data.get('next_scheduled_post_time')
    last_update_time = data.get('time_posted')

    all_countries = sorted(set(player.get('country', '').upper() for player in leaderboard if player.get('country')))
    countries_full = defaultdict(lambda: 'Unknown Country')
    for code in all_countries:
        country = countries_by_alpha2.get(code)
        if country:
            countries_full[code] = country.name

    # Преобразуем defaultdict обратно в обычный словарь для передачи в шаблон
    countries_full = dict(countries_full)

    if rank_from and rank_to:
        try:
            rank_from = int(rank_from)
            rank_to = int(rank_to)
            leaderboard = leaderboard[rank_from - 1:rank_to]
            # leaderboard = [player for player in leaderboard if rank_from <= player.get('rank') <= rank_to]
        except ValueError:
            pass

    if countries:
        selected_countries = countries.split(',')
        leaderboard = [player for player in leaderboard if
                       player.get('country') and player['country'].upper() in selected_countries]

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
            'team': team,
            'name_player': name_player,
            'countries': countries_full,
            'selected_countries': selected_countries if countries else []
        }
    )
