import pymongo
import random
import argparse
from modules.event import evt
from modules.datasrc import gen
import modules.forum as forum
import modules.util as util


def create_team_colls(
    db: pymongo.MongoClient, args: argparse.Namespace
) -> None:

    if args.drop == "team" or args.drop == "all":
        db.team.drop()
        db.team_member.drop()

    if len(gen.teams) == 0 or args.no_create:
        return

    categs: list[forum.Categ] = []
    topics: list[forum.Topic] = []
    posts: list[forum.Post] = []
    teams: list[Team] = []
    all_members: list[TeamMember] = []

    for (team_name, num_team_posts) in zip(
        gen.teams, util.random_partition(args.posts, len(gen.teams))
    ):

        t = Team(team_name)
        teams.append(t)
        evt.add_team(t.createdBy, t.createdAt, t._id, t.name)
        categs.append(forum.Categ(team_name, True))

        team_members = t.create_members()
        for m in team_members:
            if m.user != t.createdBy:
                evt.join_team(
                    m.user, util.time_since(t.createdAt), t._id, t.name
                )

        all_members.extend(team_members)

        remaining_topics = gen.topics.copy()
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
                evt.add_post(
                    p.userId,
                    p.createdAt,
                    p._id,
                    t._id,
                    t.name,
                    [u.user for u in team_members],
                )
            categs[-1].add_topic(t)

    util.bulk_write(db.f_categ, categs, append=True)
    util.bulk_write(db.f_topic, topics, append=True)
    util.bulk_write(db.f_post, posts, append=True)
    util.bulk_write(db.team, teams)
    util.bulk_write(db.team_member, all_members)


class TeamMember:
    def __init__(self, uid: str, teamId: str):
        self._id = uid + "@" + teamId
        self.team = teamId
        self.user = uid
        self.date = util.time_since_days_ago(720)


class Team:
    def __init__(self, name: str):
        self._id = util.normalize_id(name)
        self.name = name
        self.description = gen.random_topic()
        self.descPrivate = "All of our dads could beat up YOUR dad."
        self.nbMembers = 1
        self.enabled = True
        self.open = util.chance(0.5)
        self.createdAt = util.time_since_days_ago(1440)
        self.leaders = random.sample(
            gen.uids, util.rrange(1, min(len(gen.uids), 4))
        )
        self.createdBy = self.leaders[0]
        self.chat = 20  # of course chat and forum are equal to 20.
        self.forum = 20  # wtf else would they possibly be??

    def create_members(self) -> list[TeamMember]:
        users: set[str] = set(self.leaders).union(
            random.sample(gen.uids, util.rrange(2, int(len(gen.uids) / 4)))
        )
        self.nbMembers = len(users)
        return [TeamMember(user, self._id) for user in users]
