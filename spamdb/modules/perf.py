import random
import datetime
from random import randrange as rrange

# should probably be in game.py but it's here because reasons
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


class Perf:
    def __init__(self, uid: str, index: int, numGames: int, drawRatio: float, rating: int):
        self._id = uid + "/" + str(index)
        self.userId = uid
        self.perfType = index
        self.bestWins = self._results()
        self.worstLosses = self._results()

        variantVariance = random.uniform(-0.03, 0.03)  # best variable name ever
        winRatio = 0.5 + variantVariance
        r = rating + int(8000 * variantVariance)  # ass math at its best
        draw = int(numGames * random.uniform(drawRatio / 5, drawRatio))
        win = int(numGames * winRatio - draw / 2)

        self.r = r
        self.resultStreak = {"win": self._streak(), "loss": self._streak()}
        self.playStreak = {"nb": self._streak(), "time": self._streak()}

        self.count = {
            "all": numGames,
            "rated": int(numGames * random.uniform(0.7, 0.99)),
            "draw": draw,
            "win": win,
            "loss": numGames - win - draw,
            "tour": rrange(20, 150),
            "berserk": rrange(0, 50),
            "opAvg": {"avg": 1 - winRatio, "pop": rrange(10, 100)},
            "seconds": numGames * 300,
            "disconnects": rrange(2, 40),
        }

    def getRanking(self):
        return Ranking(self)

    @staticmethod
    def _streak() -> dict[str, dict]:
        max = rrange(1, 6)
        return {"max": {"v": max}, "cur": {"v": rrange(0, max)}}

    @staticmethod
    def _results() -> dict[str, list]:
        # empty for now, but hopefully one day we can make complete nonsense values for it
        return {"results": []}


class Ranking:
    def __init__(self, stat: Perf):
        self._id = stat.userId + ":" + str(stat.perfType)
        self.perf = stat.perfType
        self.rating = stat.r
        self.progress = stat.r + rrange(-40, 40)
        self.stable = True
        self.expiresAt = datetime.datetime.now() + datetime.timedelta(days=10)
