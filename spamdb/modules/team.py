import random
from dataclasses import dataclass
from modules.event import events
from modules.env import env
import modules.forum as forum
import modules.util as util


def update_team_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.team.drop()
        db.team_member.drop()
        db.team_update.drop()

    categs: list[forum.Categ] = []
    topics: list[forum.Topic] = []
    posts: list[forum.Post] = []
    teams: list[Team] = []
    all_members: list[TeamMember] = []
    team_updates: list[TeamUpdate] = []

    fixed = {util.normalize_id(f.name): f for f in _fixed_teams}
    team_names = [name for name in env.teams if util.normalize_id(name) not in fixed]
    team_names.extend(f.name for f in _fixed_teams)

    for team_name, num_team_posts in zip(
        team_names, util.random_partition(args.forum_posts, len(team_names))
    ):
        fixed_team = fixed.get(util.normalize_id(team_name))
        t = Team(team_name, fixed_team)
        teams.append(t)
        events.add_team(t.createdBy, t.createdAt, t._id, t.name)
        categs.append(forum.Categ(team_name, True))

        for _ in range(fixed_team.updates if fixed_team else util.rrange(0, 11)):
            team_updates.append(TeamUpdate(t))

        team_members = t.create_members(args.membership, fixed_team)
        for m in team_members:
            events.join_team(m.user, util.time_since(t.createdAt), t._id, t.name)
            if m.user == t.createdBy or (fixed_team and m.user in t.leaders):
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
    teams.append(Team('Lichess Swiss'))
    teams[-1].leaders = ['superadmin']
    teams[-1].nbMembers = len(env.uids)
    teams[-1].open = True
    teams[-1].flair = 'food-drink.cheese-wedge'
    all_members.extend([TeamMember(user, teams[-1]._id) for user in env.uids])

    if not args.no_create:
        util.bulk_write(db.f_categ, categs, True)
        util.bulk_write(db.f_topic, topics, True)
        util.bulk_write(db.f_post, posts, True)
        util.bulk_write(db.team, teams)
        util.bulk_write(db.team_member, all_members)
        util.bulk_write(db.team_update, team_updates)

    return teams


class TeamMember:
    def __init__(self, uid: str, teamId: str):
        self._id = uid + '@' + teamId
        self.team = teamId
        self.user = uid
        self.date = util.time_since_days_ago()


class Team:
    def __init__(self, name: str, fixed: 'FixedTeam | None' = None):
        self._id = util.normalize_id(name)
        self.name = name
        self.description = env.random_topic()
        self.descPrivate = 'All of our dads could beat up YOUR dad.'
        self.nbMembers = 1
        self.enabled = True
        self.open = util.chance(0.5)
        self.createdAt = util.time_since_days_ago()
        self.leaders = random.sample(env.uids, util.rrange(1, min(len(env.uids), 4)))
        self.createdBy = self.leaders[0]
        self.chat = 20  # of course chat and forum are equal to 20.
        self.forum = 20  # wtf else would they possibly be??
        if not fixed and util.chance(0.6):
            self.flair = env.random_flair()
        if fixed:
            self.description = fixed.description
            self.open = fixed.open
            # users can be limited with --users, and the ones that are left are the first in uids.txt
            self.leaders = [uid for uid in fixed.leaders if uid in env.uids] or env.uids[:1]
            self.createdBy = self.leaders[0]

    def create_members(self, membership: float, fixed: 'FixedTeam | None' = None) -> list[TeamMember]:
        users: list[str]
        if fixed:
            users = list(dict.fromkeys(self.leaders + [uid for uid in fixed.members if uid in env.uids]))
        else:
            users = list(set(self.leaders).union(random.sample(env.uids, int(len(env.uids) * membership))))
        self.nbMembers = len(users)
        return [TeamMember(user, self._id) for user in users]


class TeamUpdate:
    def __init__(self, team: Team):
        self._id = env.next_id(TeamUpdate)
        self.team = team._id
        self.text = env.random_team_update()
        self.sender = random.choice(team.leaders)
        self.date = util.time_since(team.createdAt)
        self.seenBy: list[str] = []


@dataclass
class FixedTeam:
    """
    A team that is created with the same leaders and members every time, unlike the other teams that
    get random ones, so that scripts and tests can count on it. The leaders can do everything with it.
    """

    name: str
    description: str
    open: bool  # anyone can join, or a leader has to accept the request
    leaders: list[str]  # the first one created the team
    members: list[str]  # besides the leaders. Nobody else is a member.
    updates: int = 3  # sent by the leaders


_fixed_teams: list[FixedTeam] = [
    FixedTeam(
        'Private Chess Club',
        'Membership requests are reviewed by the leaders of the club.',
        open=False,
        leaders=['bobby', 'mary'],
        members=['boris', 'ana', 'jiang', 'elena', 'lola'],
    ),
    FixedTeam(
        'Open Chess Club',
        'Everyone is welcome to join the club.',
        open=True,
        leaders=['bobby', 'mary'],
        members=['boris', 'ana', 'jiang', 'elena', 'lola', 'yulia', 'angel'],
    ),
]

_leader_perms: list[str] = [
    'public',
    'settings',
    'tour',
    'comm',
    'request',
    'pmall',
    'kick',
    'admin',
]
