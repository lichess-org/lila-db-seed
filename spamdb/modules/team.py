import pymongo
import random
from random import randrange as rrange
from modules.event import evt
from modules.datasrc import gen
import modules.forum as forum
import modules.util as util


def createTeamColls(db: pymongo.MongoClient, totalNumPosts: int) -> None:

    if len(gen.teams) == 0:
        return

    categs: list[forum.Categ] = []
    topics: list[forum.Topic] = []
    posts: list[forum.Post] = []
    teams: list[Team] = []
    allMembers: list[TeamMember] = []
    numTeamPostsList = util.randomPartition(totalNumPosts, len(gen.teams))

    for (teamName, numTeamPosts) in zip(gen.teams, numTeamPostsList):

        t = Team(teamName)
        teams.append(t)
        evt.addTeam(t.createdBy, t.createdAt, t._id, t.name)
        categs.append(forum.Categ(teamName, True))

        teamMembers = t.createMembers()
        for m in teamMembers:
            if m.user != t.createdBy:
                evt.joinTeam(m.user, util.timeSince(t.createdAt), t._id, t.name)

        allMembers.extend(teamMembers)

        for numPosts in util.randomPartition(numTeamPosts, int(numTeamPosts / 10) + 1):
            if numPosts == 0:
                continue
            t = forum.Topic(random.choice(gen.topics), categs[-1]._id)
            topics.append(t)
            for _ in range(numPosts):
                p = forum.Post(random.choice(teamMembers).user)
                posts.append(p)
                t.correlatePost(p)
                evt.addPost(p.userId, p.createdAt, p._id, t._id, t.name)
            categs[-1].addTopic(t)

    util.bulkwrite(db.f_categ, categs, True)
    util.bulkwrite(db.f_topic, topics, True)
    util.bulkwrite(db.f_post, posts, True)
    util.bulkwrite(db.team, teams)
    util.bulkwrite(db.team_member, allMembers)


def drop(db: pymongo.MongoClient) -> None:
    db.team.drop()
    db.team_member.drop()


class TeamMember:
    def __init__(self, userId: str, teamId: str):
        self._id = userId + "@" + teamId
        self.team = teamId
        self.user = userId
        self.date = util.timeSinceDaysAgo(720)


class Team:
    def __init__(self, name: str):
        self._id = util.normalizeId(name)
        self.name = name
        self.description = gen.randomTopic()
        self.descPrivate = "All of our dads could beat up YOUR dad."
        self.nbMembers = 1
        self.enabled = True
        self.open = util.chance(0.5)
        self.createdAt = util.timeSinceDaysAgo(1440)
        self.leaders = list(random.sample(gen.uids, (rrange(1, 4))))
        self.createdBy = self.leaders[0]
        self.chat = 20  # of course chat and forum are equal to 20.
        self.forum = 20  # wtf else would they possibly be??

    def createMembers(self) -> list[TeamMember]:
        users: set[str] = set(self.leaders).union(random.sample(gen.uids, (rrange(2, len(gen.uids) / 4))))
        self.nbMembers = len(users)
        return [TeamMember(user, self._id) for user in users]
