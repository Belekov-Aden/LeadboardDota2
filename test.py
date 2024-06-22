import pprint

import requests
import json

reqion = 'europe'

data: dict = requests.get(
    f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={reqion}&leaderboard=0').json()

pprint.pprint(data.get('leaderboard')[5])
