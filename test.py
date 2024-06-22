import pprint

import datetime
import requests
import json

reqion = 'europe'

data: dict = requests.get(
    f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={reqion}&leaderboard=0').json()

pprint.pprint(data.get('leaderboard')[1:5 + 1])

# {
#     'country': 'bg',
#     'name': 'bzm',
#     'rank': 6,
#     'sponsor': '[1pool]',
#     'team_id': 2586976,
#     'team_tag': 'OG'
# }
