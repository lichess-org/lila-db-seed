import random
from modules.env import env
import modules.util as util


def update_puzzle_colls() -> None:
    args = env.args
    db = env.db
    
    if args.drop:
        db.puzzle2_round.drop()

    puzzles: list[PuzzleItem] = []

    for uid in env.uids:
        puzzles.append(PuzzleItem(uid))

    if args.no_create:
        return
    
    util.bulk_write(db.puzzle2_round, puzzles)

class PuzzleItem:
    def __init__(self, uid: str):
        self._id = env.next_id(PuzzleItem)
        self.w = random.choice([True, False])
        self.d = util.time_since_days_ago()
        self.u = uid