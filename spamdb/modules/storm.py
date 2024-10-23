import random
from datetime import datetime
from modules.env import env
import modules.util as util


def update_storm_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.storm_day.drop()

    storms: list[StormDay] = []

    for uid in env.uids:
        storms.append(StormDay(uid))

    if args.no_create:
        return

    util.bulk_write(db.storm_day, storms)

class StormDay:
    def __init__(self, uid: str):
        self._id = f'{uid}:{(datetime.today() - datetime(2010, 1, 1)).days}' # Get the correct day integer that represents the current date
        self.score = random.randint(1, 100)
        self.moves = self.score + random.randint(0, 50)
        self.errors = random.randint(0, self.score)
        self.combo = random.randint(0, self.moves)
        self.time = random.randint(100, 255)
        self.highest = random.randint(1000, 3000)
        self.runs = random.randint(1, 10)
