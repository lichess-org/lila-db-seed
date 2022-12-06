import bson
import base64
import pymongo
import random
import argparse
from sys import stdout
from datetime import datetime
from modules.seed import env
from modules.event import events
import modules.perf as perf
import modules.util as util


def update_user_colls() -> None:
    args = env.args
    db = env.db
    do_drop = args.drop == "user" or args.drop == "all"

    if do_drop:
        db.perf_stat.drop()
        db.pref.drop()
        db.ranking.drop()
        db.history4.drop()
        db.user4.drop()

    users: list[User] = []
    rankings: list[perf.Ranking] = []
    perfs: list[perf.Perf] = []
    history: list[History] = []

    follow_factor = args.follow

    for uid in env.uids:
        users.append(User(uid))
        for stat in users[-1].detach_perfs():
            perfs.append(stat)
            rankings.append(stat.get_ranking())
        env.fide_map[uid] = users[-1].profile["fideRating"]
        history.append(History(users[-1]))

    for u in users:
        for f in random.sample(env.uids, int(follow_factor * len(env.uids))):
            events.follow(u._id, util.time_since(u.createdAt), f)

    users.extend(_create_special_users())

    if args.no_create:
        return

    util.bulk_write(db.pref, [Pref(u._id) for u in users], do_drop)
    util.bulk_write(db.user4, users, do_drop)
    util.bulk_write(db.ranking, rankings, do_drop)
    util.bulk_write(db.perf_stat, perfs, do_drop)
    util.bulk_write(db.history4, history, do_drop)


class User:
    def __init__(
        self,
        name: str,
        marks: list[str] = [],
        roles: list[str] = [],
        with_perfs: bool = True,
    ):
        self._id = util.normalize_id(name)
        self.username = name.capitalize()
        self.email = f"lichess.waste.basket+{name}@gmail.com"
        self.bpass = bson.binary.Binary(env.get_password_hash(name))
        self.enabled = True
        self.createdAt = util.time_since_days_ago(365)
        self.seenAt = util.time_since(self.createdAt)
        self.lang = "en-US"
        self.time = {"total": util.rrange(10000, 20000), "tv": 0}
        self.roles = []
        self.roles.extend(roles)
        self.marks = marks
        if util.chance(0.1):
            self.title = random.choice(_titles)
        self.plan = {
            "months": 1,
            "active": util.chance(0.2),
            "since": util.time_since_days_ago(30),
        }
        rating = min(3000, max(int(random.normalvariate(1700, 300)), 400))
        self.profile = {
            "country": env.random_country(),
            "location": self.username + " City",
            "bio": env.random_paragraph(),
            "firstName": self.username,
            "lastName": self.username + "bertson",
            "fideRating": rating,
            "uscfRating": util.rrange(rating - 200, rating + 200),
            "ecfRating": util.rrange(rating - 200, rating + 200),
            "rcfRating": util.rrange(rating - 200, rating + 200),
            "cfcRating": util.rrange(rating - 200, rating + 200),
            "dsbRating": util.rrange(rating - 200, rating + 200),
            "links": "\n".join(env.random_social_media_links()),
        }
        total_games = util.rrange(2000, 10000)
        total_wins = total_losses = total_draws = 0
        if with_perfs:
            self.perfStats = {}  # we'll detach this later
            self.perfs = {}
            perf_games: list[int] = util.random_partition(
                total_games, len(perf.types), 0
            )

            for [index, perf_name, draw_ratio], num_games in zip(
                perf.types, perf_games
            ):
                if num_games == 0:
                    continue
                p = perf.Perf(self._id, index, num_games, draw_ratio, rating)

                total_wins = total_wins + p.count["win"]
                total_losses = total_losses + p.count["loss"]
                total_draws = total_draws + p.count["draw"]
                self.perfStats[perf_name] = p
                self.perfs[perf_name] = {
                    "nb": p.count["all"],
                    "la": util.time_since_days_ago(30),
                    "re": [util.rrange(-32, 32) for _ in range(12)],
                    "gl": {
                        "r": p.r,
                        "d": random.uniform(0.5, 120),
                        "v": random.uniform(0.001, 0.1),
                    },
                }
        else:
            total_games = 0

        self.count = {
            "game": total_games,
            "ai": 0,
            "rated": int(total_games * 0.8),
            "win": total_wins,
            "winH": total_wins,
            "loss": total_losses,
            "lossH": total_losses,
            "draw": total_draws,
            "drawH": total_draws,
        }

    def detach_perfs(
        self,
    ) -> list[perf.Perf]:
        detached_list: list[perf.Perf] = list(self.perfStats.values())
        delattr(self, "perfStats")
        return detached_list


class Pref:
    def __init__(self, uid: str):
        self._id = uid
        self.is3d = False  # completely mandatory
        self.bg = env.user_bg_mode
        self.bgImg = env.random_image_link()
        self.agreement = 2
        self.submitMove = 0


class History:
    def __init__(self, u: User):
        self._id = u._id
        if not hasattr(u, "perfs"):
            return
        for (name, perf) in u.perfs.items():
            newR = u.perfs[name]["gl"]["r"]
            origR = min(3000, max(400, util.rrange(newR - 500, newR + 500)))

            self.__dict__[name] = {}
            days: int = (datetime.now() - u.createdAt).days
            for x in range(0, days, util.rrange(2, 10)):
                intermediateR = int(origR + (newR - origR) * x / max(days, 1))
                self.__dict__[name][str(x)] = util.rrange(
                    intermediateR - 100, intermediateR + 100
                )


def _create_special_users():
    users: list[User] = []
    users.append(User("lichess", [], ["ROLE_SUPER_ADMIN"], False))
    users[-1].title = "LM"
    users.append(User("admin", [], ["ROLE_ADMIN"], False))
    users.append(User("shusher", [], ["ROLE_SHUSHER"], False))
    users.append(User("hunter", [], ["ROLE_CHEAT_HUNTER"], False))
    users.append(User("puzzler", [], ["ROLE_PUZZLE_CURATOR"], False))
    users.append(User("api", [], ["ROLE_API_HOG"], False))
    users.append(User("troll", ["troll"], [], False))
    users.append(User("rankban", ["rankban"], [], False))
    users.append(User("reportban", ["reportban"], [], False))
    users.append(User("alt", ["alt"], [], False))
    users.append(User("boost", ["boost"], [], False))
    users.append(User("engine", ["engine"], [], False))
    users.append(User("coach", [], ["ROLE_COACH"], False))
    users.append(User("teacher", [], ["ROLE_TEACHER"], False))
    users.append(User("kid", [], [], False))
    users[-1].kid = True
    for i in range(10):
        users.append(User(f"bot{i}", [], [], False))
        users[-1].title = "BOT"
    users.append(User("wide", [], [], False))
    users[-1].username = "WWWWWWWWWWWWWWWWWWWW"  # widest possible i think
    users[-1].title = "WGM"
    users[-1].plan["active"] = True  # patron
    users[-1].plan["months"] = 12
    return users


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
    # "BOT",
    # "LM",
]
