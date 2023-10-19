import random
import modules.util as util
from modules.seed import env


def update_tour_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.tournament2.drop()
        db.tournament_leaderboard.drop()
        db.tournament_pairing.drop()
        db.tournament_player.drop()
        db.trophy.drop()

    if args.tours < 1:
        return

    tours: list[Tournament] = []
    pairings: list[TournamentPairing] = []
    players: list[TournamentPlayer] = []
    leaderboards: list[TournamentLeaderboard] = []
    trophies: list[Trophy] = []

    for _ in range(args.tours):
        t = Tournament()
        tours.append(t)

        pids = random.sample(env.uids, t.nbPlayers)
        random.shuffle(pids)
        t.winner = pids[0]
        trophies.append(Trophy(t.winner))
        for (pid, index) in zip(pids, range(t.nbPlayers)):
            tp = TournamentPlayer(pid, t._id)
            players.append(tp)

            for oppIndex in range(index + 1, t.nbPlayers):
                pairings.append(TournamentPairing(pid, pids[oppIndex], t))

            tlb = TournamentLeaderboard(pid, index + 1, t)
            leaderboards.append(tlb)

    # award some more trophies, everyone wins.  well done all!
    for _ in range(len(env.uids) * 2):
        trophies.append(Trophy(env.random_uid()))

    if args.no_create:
        return

    util.bulk_write(db.trophy, trophies)
    util.bulk_write(db.tournament2, tours)
    util.bulk_write(db.tournament_leaderboard, leaderboards)
    util.bulk_write(db.tournament_pairing, pairings)
    util.bulk_write(db.tournament_player, players)


class Tournament:
    def __init__(self):
        self._id = env.next_id(Tournament)
        freq = random.choice(list(_frequency.keys()))
        speed = random.choice(list(_speed.keys()))
        self.name = f"{freq.capitalize()} {speed.capitalize()}"
        self.status = 30
        self.clock = {"limit": 30, "increment": 0}
        self.minutes = random.choice([20, 30, 40, 60, 90, 120])
        self.schedule = {"freq": freq, "speed": speed}
        self.nbPlayers = min(len(env.uids), util.rrange(4, 32))
        self.createdAt = util.time_since_days_ago()
        self.startsAt = util.time_shortly_after(self.createdAt)
        # self.featured


class TournamentPlayer:
    def __init__(self, uid: str, tid: str):
        self._id = env.next_id(TournamentPlayer)
        self.uid = uid
        self.tid = tid
        self.r = env.fide_map[uid]
        self.s = util.rrange(0, 35)
        self.m = self.s * 10000
        self.f = util.chance(self.s / 64)
        self.e = self.r + util.rrange(-200, 200)
        # self.t = # team id
        # self.w = # withdraw bool


class TournamentPairing:
    def __init__(self, p1: str, p2: str, t: Tournament):
        self._id = env.next_id(TournamentPairing)
        self.u = [p1, p2]
        self.tid = t._id
        self.s = util.rrange(30, 35)
        self.d = util.time_shortly_after(t.startsAt)
        self.t = util.rrange(10, 70)
        self.b1 = self.b2 = False


class TournamentLeaderboard:
    def __init__(self, uid: str, place: int, t: Tournament):
        self._id = env.next_id(TournamentLeaderboard)
        self.u = uid
        self.t = t._id
        self.s = (t.nbPlayers - place) * 2
        self.d = t.startsAt
        self.r = place
        self.w = self.r * 25000
        self.f = t.schedule["freq"]
        self.p = t.schedule["speed"]
        self.v = 1


# TODO: move Trophy and TrophyKind into tournament?
class Trophy:
    def __init__(self, uid: str):
        self._id = env.next_id(Trophy)
        self.user = uid
        self.kind = random.choice(_trophyKind)
        self.date = util.time_since_days_ago()


# class TrophyKind: use bin/mongodb/create-trophy-kinds.js for now

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


_trophyKind: list[str] = [
    "marathonWinner",
    "marathonTopTen",
    "marathonTopFifty",
    "marathonTopHundred",
    "marathonTopFiveHundred",
    "moderator",
    "developer",
    "verified",
    "contentTeam",
    "zugMiracle",
]
