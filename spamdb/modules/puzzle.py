import random
from modules.env import env
import modules.util as util


def update_puzzle_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.puzzle2_round.drop()

    puzzles: list[PuzzleRound] = []

    for uid in env.uids:
        sample_puzzles = random.sample(env.puzzles, 10)
        for i in range(10):
            pid = f"{uid}:{sample_puzzles[i].get('_id')}"
            puzzles.append(PuzzleRound(uid, pid))

    if args.no_create:
        return

    util.bulk_write(db.puzzle2_round, puzzles)

class PuzzleRound:
    def __init__(self, uid: str, pid: str):
        self._id = pid
        self.w = random.choice([True, False])
        self.d = util.time_since_days_ago(10)
        self.u = uid