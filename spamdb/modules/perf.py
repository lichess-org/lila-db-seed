import random
import datetime
import modules.util as util

types: list[list[int, str, float]] = [
    [0, "ultrabullet", 0.05],
    [1, "bullet", 0.1],
    [2, "blitz", 0.2],
    [3, "classical", 0.5],
    [4, "correspondence", 0.5],
    [5, "standard", 0.5],
    [6, "rapid", 0.4],
    [11, "chess960", 0.05],
    [12, "kingOfTheHill", 0.0],
    [13, "antichess", 0.1],
    [14, "atomic", 0.1],
    [15, "threeCheck", 0.01],
    [16, "horde", 0.1],
    [17, "racingkings", 0.15],
    [18, "crazyhouse", 0.01],
    [20, "puzzle", 0.0],
]


def clock_to_perf(init: int, inc: int) -> int:
    # incorrectly map clock to perf type, just to reinforce that this is shit data
    return 1 if init < 3 else 2 if init < 8 else 6 if init < 21 else 3 if init < 181 else 4

class UserPerfs:
    def __init__(
        self,
        uid: str,
        perfs: dict
    ):
        self._id = uid
        for k, v in perfs.items():
            self.__dict__[k] = v

class PerfStat:
    def __init__(
        self,
        uid: str,
        index: int,
        num_games: int,
        draw_ratio: float,
        rating: int,
    ):
        self._id = uid + "/" + str(index)
        self.userId = uid
        self.perfType = index
        self.bestWins = self._results()
        self.worstLosses = self._results()

        variant_variance = random.uniform(-0.03, 0.03)  # best variable name ever
        win_ratio = 0.5 + variant_variance
        r = rating + int(8000 * variant_variance)  # ass math at its best
        draw = int(num_games * random.uniform(draw_ratio / 5, draw_ratio))
        win = int(num_games * win_ratio - draw / 2)

        self.r = r
        self.resultStreak = {"win": self._streak(), "loss": self._streak()}
        self.playStreak = {"nb": self._streak(), "time": self._streak()}

        self.count = {
            "all": num_games,
            "rated": int(num_games * random.uniform(0.7, 0.99)),
            "draw": draw,
            "win": win,
            "loss": num_games - win - draw,
            "tour": util.rrange(20, 150),
            "berserk": util.rrange(0, 50),
            "opAvg": {"avg": 1 - win_ratio, "pop": util.rrange(10, 100)},
            "seconds": num_games * 300,
            "disconnects": util.rrange(2, 40),
        }

    def get_ranking(self):
        return Ranking(self)

    @staticmethod
    def _streak() -> dict[str, dict]:
        max = util.rrange(1, 6)
        return {"max": {"v": max}, "cur": {"v": util.rrange(0, max)}}

    @staticmethod
    def _results() -> dict[str, list]:
        # empty for now, but hopefully one day we can make complete nonsense values for it
        return {"results": []}


class Ranking:
    def __init__(self, stat: PerfStat):
        self._id = stat.userId + ":" + str(stat.perfType)
        self.perf = stat.perfType
        self.rating = stat.r
        self.progress = stat.r + util.rrange(-40, 40)
        self.stable = True
        self.expiresAt = datetime.datetime.now() + datetime.timedelta(days=10)
