import pymongo
import random
from datetime import datetime
from modules.event import evt
from modules.datasrc import gen
import modules.util as util


def create_forum_colls(db: pymongo.MongoClient, num_posts: int) -> None:

    if num_posts < 1:
        return

    categs: dict[str, Categ] = {}
    topics: list[Topic] = []
    posts: list[Post] = []

    for cat_name in gen.categs:
        categ = Categ(cat_name)
        categs[categ._id] = categ
    for topic_name in gen.topics:
        topics.append(Topic(topic_name, random.choice(list(categs.keys()))))
    for _ in range(num_posts):
        p = Post(gen.random_uid())
        posts.append(p)
        t = random.choice(topics)
        t.correlate_post(p)
        evt.add_post(p.userId, p.createdAt, p._id, t._id, t.name)

    for t in topics:
        if hasattr(t, "lastPostId"):
            categs[t.categId].add_topic(t)

    util.bulk_write(db.f_categ, categs.values())
    util.bulk_write(db.f_topic, topics)
    util.bulk_write(db.f_post, posts)


def drop(db: pymongo.MongoClient) -> None:
    db.f_categ.drop()
    db.f_topic.drop()
    db.f_post.drop()


class Post:
    def __init__(self, uid: str):
        self._id = gen.next_id(Post)
        self.text = gen.random_paragraph()
        self.troll = False
        self.hidden = False
        self.createdAt = datetime.now()
        self.userId = uid


class Topic:
    def __init__(self, name: str, categ_id: str):
        self._id = gen.next_id(Topic)
        self.name = name
        self.slug = util.normalize_id(name)
        self.categId = categ_id
        self.createdAt = util.time_since_days_ago(180)
        self.updatedAt = self.updatedAtTroll = self.createdAt
        self.nbPosts = self.nbPostsTroll = 0
        self.troll = False
        self.hidden = False
        self.closed = util.chance(0.1)
        self.userId = gen.random_uid()

    # keep the refs and sequencing fields consistent
    def correlate_post(self, p: Post):
        self.lastPostId = self.lastPostIdTroll = p._id
        self.updatedAt = (
            self.updatedAtTroll
        ) = p.createdAt = util.time_shortly_after(self.updatedAt)
        self.nbPosts = self.nbPostsTroll = self.nbPosts + 1
        p.topicId = self._id
        p.categId = self.categId
        p.number = self.nbPosts


class Categ:
    def __init__(self, name: str, team: bool = False):
        self._id = ("team-" if team else "") + util.normalize_id(name)
        self.name = name
        self.desc = gen.random_topic()
        self.nbTopics = 0
        self.nbPosts = 0
        self.nbTopicsTroll = 0
        self.nbPostsTroll = 0
        self.quiet = False
        self.lastPostAt = datetime.fromtimestamp(0.0)
        #       ^ lila doesn't used this field, but it helps us
        if team:
            self.team = util.normalize_id(name)

    # don't actually store a topic here, just keep the refs and sequencing
    # fields consistent
    def add_topic(self, t: Topic):
        self.nbTopics = self.nbTopicsTroll = self.nbTopics + 1
        self.nbPosts = self.nbPostsTroll = self.nbPosts + t.nbPosts
        if t.updatedAt > self.lastPostAt:
            self.lastPostAt = t.updatedAt
            self.lastPostId = self.lastPostIdTroll = t.lastPostId