from random import randint
from modules.env import env
import modules.util as util


def update_storm_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.storm_day.drop()

    storms: list[StormRound] = []

    for uid in env.uids:
        storms.append(StormRound(uid))

    if args.no_create:
        return

    util.bulk_write(db.storm_day, storms)

class StormRound:
    def __init__(self, uid: str):
        self._id = f'{uid}:5347'
        self.score = randint(0, 100)
        self.moves = self.score + randint(0, 50)
        self.errors = randint(0, self.score)
        self.combo = randint(0, self.moves)
        self.time = randint(0, 255)
        self.highest = randint(1000, 3000)
        self.runs = randint(0, 25)
