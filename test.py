import datetime
import requests
import json
import time
import schedule


def return_time(time: int):
    return datetime.datetime.fromtimestamp(time)


update = ''


def write_data(region: str):
    data: dict = requests.get(
        f'https://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/v0001?division={region}&leaderboard=0').json()
    leaderboard = data.get('leaderboard')
    global update
    update = return_time(data.get('next_scheduled_post_time')).strptime(
        return_time(data.get('next_scheduled_post_time')).time().strftime('%H:%M'), '%H:%M').time()
    with open(f'{region}.json', 'w') as file:
        json.dump(leaderboard, file)


schedule.every().day.at("02:03").do(lambda: write_data('europe'))

while True:
    schedule.run_pending()
    time.sleep(1)
