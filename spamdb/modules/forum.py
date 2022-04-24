import pymongo
import random
from datetime import datetime
from modules.event import evt
from modules.datasrc import gen
import modules.util as util


# if someone's using these classes for anything other than spamming the database
# in one giant blast, god help them.


def createForumColls(db: pymongo.MongoClient, numPosts: int) -> None:

    if numPosts < 1:
        return

    categs: dict[str, Categ] = {}
    topics: list[Topic] = []
    posts: list[Post] = []

    for catName in gen.categs:
        categ = Categ(catName)
        categs[categ._id] = categ
    for topicName in gen.topics:
        topics.append(Topic(topicName, random.choice(list(categs.keys()))))
    for _ in range(numPosts):
        p = Post(gen.randomUid())
        posts.append(p)
        t = random.choice(topics)
        t.correlatePost(p)
        evt.addPost(p.userId, p.createdAt, p._id, t._id, t.name)

    # don't keep topics that didn't get randomly assigned any posts
    [categs[t.categId].addTopic(t) for t in topics if hasattr(t, "lastPostId")]

    # now we can write everything
    util.bulkwrite(db.f_categ, categs.values())
    util.bulkwrite(db.f_topic, topics)
    util.bulkwrite(db.f_post, posts)


def drop(db: pymongo.MongoClient) -> None:
    db.f_categ.drop()
    db.f_topic.drop()
    db.f_post.drop()


class Post:
    def __init__(self, uid: str):
        self._id = gen.nextId(Post)
        self.text = gen.randomParagraph()
        self.troll = False
        self.hidden = False
        self.createdAt = datetime.now()
        self.userId = uid


class Topic:
    def __init__(self, name: str, categId: str):
        self._id = gen.nextId(Topic)
        self.name = name
        self.slug = util.normalizeId(name)
        self.categId = categId
        self.createdAt = util.timeSinceDaysAgo(180)
        self.updatedAt = self.updatedAtTroll = self.createdAt
        self.nbPosts = self.nbPostsTroll = 0
        self.troll = False
        self.hidden = False
        self.closed = util.chance(0.1)
        self.userId = gen.randomUid()

    # keep the refs and sequencing fields consistent
    def correlatePost(self, p: Post):
        self.lastPostId = self.lastPostIdTroll = p._id
        self.updatedAt = self.updatedAtTroll = p.createdAt = util.timeShortlyAfter(self.updatedAt)
        self.nbPosts = self.nbPostsTroll = self.nbPosts + 1
        p.topicId = self._id
        p.categId = self.categId
        p.number = self.nbPosts


class Categ:
    def __init__(self, name: str, team: bool = False):
        self._id = ("team-" if team else "") + util.normalizeId(name)
        self.name = name
        self.desc = gen.randomTopic()
        self.nbTopics = 0
        self.nbPosts = 0
        self.nbTopicsTroll = 0
        self.nbPostsTroll = 0
        self.quiet = False
        self.lastPostAt = datetime.fromtimestamp(0.0)
        #       ^ lila doesn't used this field, but it helps us
        if team:
            self.team = util.normalizeId(name)

    # don't actually store a topic here, just keep the refs and sequencing fields consistent
    def addTopic(self, t: Topic):
        self.nbTopics = self.nbTopicsTroll = self.nbTopics + 1
        self.nbPosts = self.nbPostsTroll = self.nbPosts + t.nbPosts
        if t.updatedAt > self.lastPostAt:
            self.lastPostAt = t.updatedAt
            self.lastPostId = self.lastPostIdTroll = t.lastPostId
