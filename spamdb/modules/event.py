import enum
import bson
import pymongo
from random import randrange as rrange
from datetime import datetime
import modules.util as util
from modules.datasrc import gen


def create_event_colls(db: pymongo.MongoClient) -> None:
    activities: list[dict] = []
    relations: list[Relation] = []

    for (days, udicts) in sorted(evt.activity_map.items()):
        activities.extend(udicts.values())
    for uid in evt.relation_map.keys():
        relations.extend([Relation(uid, f) for f in evt.relation_map[uid]])

    util.bulk_write(db.relation, relations)
    util.bulk_write(db.activity2, activities)
    util.bulk_write(db.timeline_entry, evt.timeline)


def drop(db: pymongo.MongoClient) -> None:
    db.activity2.drop()
    db.timeline_entry.drop()
    db.relation.drop()


# handles activity and timeline collections
class EventApi:
    def __init__(self):
        self.relation_map: dict[str, list[str]] = {}
        self.activity_map: dict[int, dict[str, dict]] = {}
        self.history_map: dict[str, History] = {}
        self.timeline: list = []

    class Outcome(enum.Enum):
        DRAW = enum.auto()
        WIN = enum.auto()
        LOSS = enum.auto()

        def invert(self):
            return {
                self.WIN: self.LOSS,
                self.LOSS: self.WIN,
                self.DRAW: self.DRAW,
            }

    def follow(self, uid: str, time: datetime, following: str) -> None:
        if uid == following:
            return
        self.relation_map.setdefault(uid, []).append(following)
        self.timeline.append(
            TimelineEntry(time, self.relation_map[uid]).follow(uid, following)
        )
        f = self._lazy_make_activity(uid, time, "f", [])
        # wtf here

    def add_post(
        self, uid: str, time: datetime, pid: str, tid: str, tname: str
    ) -> None:
        self.timeline.append(
            TimelineEntry(time, self.relation_map[uid]).forum_post(
                uid, pid, tid, tname
            )
        )
        self._lazy_make_activity(uid, time, "p", []).append(pid)

    def add_team(self, uid: str, time: datetime, tid: str, tname: str) -> None:
        self.timeline.append(
            TimelineEntry(time, self.relation_map[uid]).team_create(uid, tid)
        )
        self._lazy_make_activity(uid, time, "e", []).append(tname)

    def join_team(
        self, uid: str, time: datetime, tid: str, tname: str
    ) -> None:
        self.timeline.append(
            TimelineEntry(time, self.relation_map[uid]).team_join(uid, tid)
        )
        self._lazy_make_activity(uid, time, "e", []).append(tname)

    def add_game(
        self,
        uid: str,
        time: datetime,
        opponent: str,
        outcome: Outcome,
        pid: str,
    ) -> None:
        self.timeline.append(
            TimelineEntry(time, [uid]).game_end(
                opponent, outcome == self.Outcome.WIN, pid
            )
        )
        self._game_activity(uid, time, outcome)
        self._game_activity(opponent, time, outcome.invert())

    def _game_activity(
        self, uid: str, time: datetime, outcome: Outcome
    ) -> None:
        v = self._lazy_make_activity(uid, time, "g", {}).setdefault(
            "standard",
            {
                "w": 0,
                "l": 0,
                "d": 0,
                "r": [gen.fide_map[uid], gen.fide_map[uid]],
            },
        )
        if outcome == self.Outcome.DRAW:
            v["d"] = v["d"] + 1
            v["r"][1] = v["r"][1] + 5
        elif outcome == self.Outcome.WIN:
            v["w"] = v["w"] + 1
            v["r"][1] = v["r"][1] + 10
        else:
            v["l"] = v["l"] + 1
            v["r"][1] = v["r"][1] - 10

    def _lazy_make_activity(self, uid: str, time: datetime, key: str, default):
        days = util.days_since_genesis(time)
        activity = self.activity_map.setdefault(days, {}).setdefault(
            uid, Activity(uid, days)
        )
        if not hasattr(activity, key):
            setattr(activity, key, default)
        return getattr(activity, key)


evt = EventApi()


class Relation:
    def __init__(self, uid: str, follows: str, friend: bool = True):
        self._id = f"{uid}/{follows}"
        self.u1 = uid
        self.u2 = follows
        self.r = friend


class Activity:
    def __init__(self, id: str, days: int):
        self._id = f"{id}:{days}"


class TimelineEntry:
    def __init__(self, time: datetime, listeners: list[str]):
        self._id = bson.ObjectId()
        self.date = time
        self.users = listeners

    def game_end(self, opponent: str, win: bool, pid: str):
        self.typ = "game-end"
        self.data = {
            "playerId": pid,
            "perf": "standard",
            "opponent": opponent,
            "win": win,
        }
        self.chan = "gameEnd"
        return self

    def forum_post(self, uid: str, pid: str, tid: str, tname: str):
        self.typ = "forum-post"
        self.data = {
            "userId": uid,
            "topicName": tname,
            "postId": pid,
            "topicId": tid,
        }
        self.chan = f"forum:{tid}"
        return self

    def follow(self, uid: str, following: str):
        self.typ = "follow"
        self.data = {"u1": uid, "u2": following}
        self.chan = "follow"
        return self

    def team_create(self, uid: str, tid: str):
        self.typ = "team-create"
        self.data = {"userId": uid, "teamId": tid}
        self.chan = "teamCreate"
        return self

    def team_join(self, uid: str, tid: str):
        self.typ = "team-join"
        self.data = {"userId": uid, "teamId": tid}
        self.chan = "teamJoin"
        return self

    def blog_like(self, uid: str, bid: str, title: str):
        self.typ = "ublog-post-like"
        self.data = {"userId": uid, "id": bid, "title": title}
        self.chan = "ublogPostLike"
        return self

    #    "follow"          -> toBson(d)
    #   case d: TeamJoin      => "team-join"       -> toBson(d)
    #   case d: TeamCreate    => "team-create"     -> toBson(d)
    #   case d: ForumPost     => "forum-post"      -> toBson(d)
    #   case d: UblogPost     => "ublog-post"      -> toBson(d)
    #   case d: TourJoin      => "tour-join"       -> toBson(d)
    #   case d: GameEnd       => "game-end"        -> toBson(d)
    #   case d: SimulCreate   => "simul-create"    -> toBson(d)
    #   case d: SimulJoin     => "simul-join"      -> toBson(d)
    #   case d: StudyLike     => "study-like"      -> toBson(d)
    #   case d: PlanStart     => "plan-start"      -> toBson(d)
    #   case d: PlanRenew     => "plan-renew"      -> toBson(d)
    #   case d: BlogPost      => "blog-post"       -> toBson(d)
    #   case d: UblogPostLike => "ublog-post-like" -> toBson(d)
    #   case d: StreamStart   => "stream-start"    -> toBson(d)
