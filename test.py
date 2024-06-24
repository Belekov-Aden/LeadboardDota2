import datetime
import requests
import json
import time
import schedule
from threading import Thread


def return_time(timestamp: int):
    return datetime.datetime.fromtimestamp(timestamp)


update = ''  # Начальное фиксированное время


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


def scheduler_thread():
    schedule.every().day.at("20:28").do(write_data)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Запуск фонового потока с расписанием
thread = Thread(target=scheduler_thread, daemon=True)
thread.start()

# Пример бесконечного цикла, чтобы фоновый поток продолжал работать
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Программа остановлена")
