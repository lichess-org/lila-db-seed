import bson
import base64
import pymongo
import random
import datetime
from random import randrange as rrange
from modules.datasrc import gen
from modules.event import evt
import modules.perf as perf
import modules.pref as pref
import modules.util as util


def createUserColls(db: pymongo.MongoClient, followFactor: float) -> None:

    users: list[User] = []
    rankings: list[perf.Ranking] = []
    perfs: list[perf.Perf] = []
    relations: list[Relation] = []
    history: list[History] = []
    fideMap = {}

    for uid in gen.uids:
        users.append(User(uid))
        for stat in users[-1].detachPerfs():
            perfs.append(stat)
            rankings.append(stat.getRanking())
        gen.fideMap[uid] = users[-1].profile["fideRating"]
        history.append(History(users[-1]))

    users.extend(User.createSpecialUsers())
    for u in users:
        for f in random.sample(gen.uids, int(followFactor * len(gen.uids))):
            evt.follow(u._id, util.timeSince(u.createdAt), f)

    util.bulkwrite(db.pref, [pref.Pref(u._id) for u in users])
    util.bulkwrite(db.user4, users)
    util.bulkwrite(db.ranking, rankings)
    util.bulkwrite(db.perf_stat, perfs)
    util.bulkwrite(db.history4, history)


def drop(db: pymongo.MongoClient) -> None:
    db.perf_stat.drop()
    db.pref.drop()
    db.ranking.drop()
    db.history4.drop()
    db.user4.drop()


class User:
    def __init__(self, name: str, marks: list[str] = [], roles: list[str] = [], withPerfs: bool = True):
        self._id = util.normalizeId(name)
        self.username = name.capitalize()
        self.email = f"lichess.waste.basket+{name}@gmail.com"
        self.bpass = bson.binary.Binary(base64.b64decode("E11iacfUn7SA1X4pFDRi+KkX8kT2XnckW6kx+w5AY7uJet8q9mGv"))
        self.enabled = True
        self.createdAt = util.timeSinceDaysAgo(365)
        self.seenAt = util.timeSince(self.createdAt)
        self.lang = "en-US"
        self.time = {"total": rrange(10000, 20000), "tv": 0}
        self.roles = ["ROLE_VERIFIED"]
        self.roles.extend(roles)
        self.marks = marks
        self.kid = util.chance(0.05)
        if util.chance(0.1):
            self.title = random.choice(_titles)
        self.plan = {
            "months": 1,
            "active": util.chance(0.2),
            "since": util.timeSinceDaysAgo(30),
        }
        rating = min(3000, max(int(random.normalvariate(1700, 300)), 400))
        self.profile = {
            "country": gen.randomCountry(),
            "location": self.username + " City",
            "bio": gen.randomParagraph(),
            "firstName": self.username,
            "lastName": self.username + "bertson",
            "fideRating": rating,
            "uscfRating": rrange(rating - 200, rating + 200),
            "ecfRating": rrange(rating - 200, rating + 200),
            "rcfRating": rrange(rating - 200, rating + 200),
            "cfcRating": rrange(rating - 200, rating + 200),
            "dsbRating": rrange(rating - 200, rating + 200),
            "links": "\n".join(gen.randomSocialMediaLinks()),
        }
        totalGames = rrange(2000, 10000)
        totalWins = totalLosses = totalDraws = 0
        if withPerfs:
            self.perfStats = {}  # we'll detach this later
            self.perfs = {}
            perfGames: list[int] = util.randomPartition(totalGames, len(perf.types), 0)

            for [index, perfName, drawRatio], numGames in zip(perf.types, perfGames):
                if numGames == 0:
                    continue
                p = perf.Perf(self._id, index, numGames, drawRatio, rating)

                totalWins = totalWins + p.count["win"]
                totalLosses = totalLosses + p.count["loss"]
                totalDraws = totalDraws + p.count["draw"]
                self.perfStats[perfName] = p
                self.perfs[perfName] = {
                    "nb": p.count["all"],
                    "la": util.timeSinceDaysAgo(30),
                    "re": [rrange(-32, 32) for _ in range(12)],
                    "gl": {
                        "r": p.r,
                        "d": random.uniform(0.5, 120),
                        "v": random.uniform(0.001, 0.1),
                    },
                }
        else:
            totalGames = 0

        self.count = {
            "game": totalGames,
            "ai": 0,
            "rated": int(totalGames * 0.8),
            "win": totalWins,
            "winH": totalWins,
            "loss": totalLosses,
            "lossH": totalLosses,
            "draw": totalDraws,
            "drawH": totalDraws,
        }

    def detachPerfs(self) -> list[perf.Perf]:  # build perfs here, but they aren't stored in user4
        detachedList: list[perf.Perf] = list(self.perfStats.values())
        delattr(self, "perfStats")
        return detachedList

    @staticmethod
    def createSpecialUsers():
        users: list[User] = []
        users.append(User("lichess", [], ["ROLE_SUPER_ADMIN"], False))
        users[-1].title = "LM"
        users.append(User("admin", [], ["ROLE_ADMIN"], False))
        users.append(User("shusher", [], ["ROLE_SHUSHER"], False))
        users.append(User("cheat-hunter", [], ["ROLE_CHEAT_HUNTER"], False))
        users.append(User("boost-hunter", [], ["ROLE_BOOST_HUNTER"], False))
        users.append(User("timeout-mod", [], ["ROLE_TIMEOUT_MOD"], False))
        users.append(User("puzzle-curator", [], ["ROLE_PUZZLE_CURATOR"], False))
        users.append(User("api-hog", [], ["ROLE_API_HOG"], False))
        users.append(User("troll", ["troll"], [], False))
        users.append(User("rank-ban", ["rankban"], [], False))
        users.append(User("report-ban", ["reportban"], [], False))
        users.append(User("alt", ["alt"], [], False))
        users.append(User("boost", ["boost"], [], False))
        users.append(User("engine", ["engine"], [], False))
        users.append(User("kid", [], ["ROLE_VERIFIED"], False))
        users[-1].kid = True
        users.append(User("unverified", [], [], False))
        users[-1].roles = []
        users.append(User("bot", [], ["ROLE_VERIFIED"], False))
        users[-1].title = "BOT"
        users.append(User("wide", [], ["ROLE_VERIFIED"], False))  # for ui testing
        users[-1].username = "WWWWWWWWWWWWWWWWWWWW"  # widest possible i think
        users[-1].title = "WGM"
        users[-1].plan["active"] = True  # patron
        users[-1].plan["months"] = 12
        return users


class History:
    def __init__(self, u: User):
        self._id = u._id
        if not hasattr(u, "perfs"):
            return
        for (name, perf) in u.perfs.items():

            newR = u.perfs[name]["gl"]["r"]
            origR = min(3000, max(400, rrange(newR - 500, newR + 500)))  # used to be sooo much better/worse!

            self.__dict__[name] = {}
            days: int = (datetime.datetime.now() - u.createdAt).days
            for x in range(0, days, rrange(2, 10)):
                intermediateR = int(origR + (newR - origR) * x / max(days, 1))
                self.__dict__[name][str(x)] = rrange(intermediateR - 100, intermediateR + 100)


_titles: list[str] = [
    "GM",
    "WGM",
    "IM",
    "WIM",
    "FM",
    "WFM",
    "NM",
    "CM",
    "WCM",
    "WNM",
    "BOT"
    # "LM"
]
