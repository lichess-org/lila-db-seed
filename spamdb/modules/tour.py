import pymongo
import random
from datetime import datetime
import modules.util as util
from modules.datasrc import gen
from modules.event import evt


#   for each tournament, tracks tournament name, status, clock {limit: secs, increment: secs}
#   length, number of players, conditions: { nbRatedGame {nb: 20, perf: <perf-type>},
#   creation date, starts at, winner, schedule: {freq: hourly, speed: rapid/classical },
#   and an id called "featured" which is a gameId i believe (dangerous to fabricate/map?)


def create_tour_colls(db: pymongo.MongoClient, num_tours: int) -> None:
    if num_tours == 0:
        return

    tours: list[Tournament] = []
    pairings: list[TournamentPairing] = []
    players: list[TournamentPlayer] = []
    leaderboards: list[TournamentLeaderboard] = []

    for _ in range(num_tours):
        t = Tournament()
        tours.append(t)
        pids = random.sample(gen.uids, t.nbPlayers)
        t.winner = random.choice(pids)
        for pid in players:
            tplay = TournamentPlayer(pid, t._id)
            players.append(tplay)
            others = [oid for oid in pids if oid != pid]
            tpair = TournamentPairing(
                pid, random.choice(others), t._id, t.startsAt
            )
            pairings.append(tpair)
            tlb = TournamentLeaderboard(pid, t)
            leaderboards.append(tlb)

    util.bulk_write(db.tournament2, tours)
    util.bulk_write(db.tournament_leaderboard, leaderboards)
    util.bulk_write(db.tournament_pairing, pairings)
    util.bulk_write(db.tournament_player, players)


def drop(db: pymongo.MongoClient) -> None:
    db.tournament2.drop()
    db.tournament_leaderboard.drop()
    db.tournament_pairing.drop()
    db.tournament_player.drop()


class Tournament:
    def __init__(self):
        self._id = gen.next_id(Tournament)
        perf = "bullet"
        freq = random.choice(list(_frequency.keys()))
        self.name = f"{freq.capitalize()} {perf.capitalize()}"
        self.status = 30
        self.clock = {"limit": 30, "increment": 0}
        self.minutes = 30
        self.schedule = {"freq": freq, "speed": perf}
        self.nbPlayers = util.rrange(4, 32)
        self.createdAt = util.time_since_days_ago(365)
        self.startsAt = util.time_shortly_after(self.createdAt)
        # self.featured
        self.winner = gen.random_uid()


class TournamentPlayer:
    def __init__(self, uid: str, tid: str):
        self._id = gen.next_id(TournamentPlayer)
        self.uid = uid
        self.tid = tid
        self.r = gen.fide_map[uid]
        self.s = util.rrange(0, 32)
        self.m = self.s * 10017
        self.f = util.chance(self.s / 64)
        self.e = self.r + util.rrange(-200, 200)
        # self.t = # team id
        # self.w = # withdraw bool


class TournamentPairing:
    def __init__(self, p1: str, p2: str, tid: str, time: datetime):
        self._id = gen.next_id(TournamentPairing)
        self.u = [p1, p2]
        self.t = tid
        self.s = util.rrange(30, 35)
        self.d = time
        self.t = util.rrange(10, 70)
        self.b1 = self.b2 = False


class TournamentLeaderboard:
    def __init__(self, uid: str, tour: Tournament):
        self._id = gen.next_id(TournamentLeaderboard)
        self.uid = uid
        self.tid = tour._id
        self.s = util.rrange(0, 32)
        self.d = tour.startsAt
        self.r = (
            1 if uid == tour.winner else util.rrange(2, tour.nbPlayers + 1)
        )
        self.w = self.r * 25000
        self.f = _frequency[tour.schedule["freq"]]
        self.p = _speed[tour.schedule["speed"]]
        self.v = 1


#  case object Created       extends Status(10)
#   case object Started       extends Status(20)
#   case object Aborted       extends Status(25) // from this point the game is finished
#   case object Mate          extends Status(30)
#   case object Resign        extends Status(31)
#   case object Stalemate     extends Status(32)
#   case object Timeout       extends Status(33) // when player leaves the game
#   case object Draw          extends Status(34)
#   case object Outoftime     extends Status(35) // clock flag
#   case object Cheat         extends Status(36)
#   case object NoStart       extends Status(37) // the player did not make the first move in time
#   case object UnknownFinish extends Status(38) // we don't know why the game ended
#   case object VariantEnd    extends Status(60) // the variant has a special ending

_speed: dict[str, int] = {
    "ultrabullet": 5,
    "hyperbullet": 10,
    "bullet": 20,
    "hippobullet": 25,
    "superblitz": 30,
    "blitz": 40,
    "rapid": 50,
    "casual": 60,
}

_frequency: dict[str, int] = {
    "hourly": 10,
    "daily": 20,
    "eastern": 30,
    "weekly": 40,
    "monthly": 50,
    "shield": 51,
    "marathon": 60,
    "yearly": 70,
    "unique": 90,
}

_status: list[int] = [
    10,  # created
    20,  # started
    30,  # finished
]
