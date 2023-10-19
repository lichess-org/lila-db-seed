import random
from modules.event import events
from modules.seed import env
import modules.forum as forum
import modules.util as util


def update_team_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.team.drop()
        db.team_member.drop()

    categs: list[forum.Categ] = []
    topics: list[forum.Topic] = []
    posts: list[forum.Post] = []
    teams: list[Team] = []
    all_members: list[TeamMember] = []

    for (team_name, num_team_posts) in zip(
        env.teams, util.random_partition(args.forum_posts, len(env.teams))
    ):
        t = Team(team_name)
        teams.append(t)
        events.add_team(t.createdBy, t.createdAt, t._id, t.name)
        categs.append(forum.Categ(team_name, True))

        team_members = t.create_members(args.membership)
        for m in team_members:
            events.join_team(m.user, util.time_since(t.createdAt), t._id, t.name)
            if m.user == t.createdBy:
                setattr(m, 'perms', _leader_perms)
            elif m.user in t.leaders:
                setattr(m, 'perms', random.sample(_leader_perms, util.rrange(1, len(_leader_perms))))
        all_members.extend(team_members)
        remaining_topics = env.topics.copy()
        random.shuffle(remaining_topics)
        for num_posts in util.random_partition(
            num_team_posts,
            min(int(num_team_posts / 10) + 1, len(remaining_topics)),
        ):
            if num_posts == 0:
                continue
            t = forum.Topic(remaining_topics.pop(), categs[-1]._id)
            topics.append(t)
            for _ in range(num_posts):
                p = forum.Post(random.choice(team_members).user)
                posts.append(p)
                t.correlate_post(p)
                events.add_post(
                    p.userId,
                    p.createdAt,
                    p._id,
                    t._id,
                    t.name,
                    [u.user for u in team_members],
                )
            categs[-1].add_topic(t)
    teams.append(Team("Lichess Swiss"))
    teams[-1].leaders = ["superadmin"]
    teams[-1].nbMembers = len(env.uids)
    teams[-1].open = True
    all_members.extend([TeamMember(user, teams[-1]._id) for user in env.uids])

    if not args.no_create:
        util.bulk_write(db.f_categ, categs, True)
        util.bulk_write(db.f_topic, topics, True)
        util.bulk_write(db.f_post, posts, True)
        util.bulk_write(db.team, teams)
        util.bulk_write(db.team_member, all_members)

    return teams


class TeamMember:
    def __init__(self, uid: str, teamId: str):
        self._id = uid + "@" + teamId
        self.team = teamId
        self.user = uid
        self.date = util.time_since_days_ago()


class Team:
    def __init__(self, name: str):
        self._id = util.normalize_id(name)
        self.name = name
        self.description = env.random_topic()
        self.descPrivate = "All of our dads could beat up YOUR dad."
        self.nbMembers = 1
        self.enabled = True
        self.open = util.chance(0.5)
        self.createdAt = util.time_since_days_ago()
        self.leaders = random.sample(env.uids, util.rrange(1, min(len(env.uids), 4)))
        self.createdBy = self.leaders[0]
        self.chat = 20  # of course chat and forum are equal to 20.
        self.forum = 20  # wtf else would they possibly be??

    def create_members(self, membership: float) -> list[TeamMember]:
        users: set[str] = set(self.leaders).union(
            random.sample(env.uids, int(len(env.uids) * membership))
        )
        self.nbMembers = len(users)
        return [TeamMember(user, self._id) for user in users]

_leader_perms: list[str] = [
    "public",
    "settings",
    "tour",
    "comm",
    "request",
    "pmall",
    "kick",
    "admin"
]
