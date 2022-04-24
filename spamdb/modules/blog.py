import pymongo
import random
from datetime import datetime
from datetime import timedelta
from random import randrange as rrange
from modules.event import evt
from modules.datasrc import gen
import modules.util as util


def createBlogColls(db: pymongo.MongoClient, numBlogs: int) -> None:
    ublogs: list = []
    uposts: list = []

    for (numPosts, uid) in zip(util.randomPartition(numBlogs, len(gen.uids), 0), gen.uids):
        if numPosts == 0:
            continue
        ublogs.append(UBlog(uid))
        for _ in range(numPosts):
            uposts.append(UBlogPost(uid))

    util.bulkwrite(db.ublog_blog, ublogs)
    util.bulkwrite(db.ublog_post, uposts)


def drop(db: pymongo.MongoClient) -> None:
    db.ublog_blog.drop()
    db.ublog_post.drop()


class UBlog:
    def __init__(self, uid: str):
        self._id = f"user:{uid}"
        self.tier = 2


_blogTopics: list[str] = [
    "Chess",
    "Analysis",
    "Puzzle",
    "Opening",
    "Endgame",
    "Tactics",
    "Strategy",
    "Chess engine",
    "Chess bot",
    "Chess Personalities",
    "Over the board",
    "Tournament",
    "Chess variant",
    "Software Development",
    "Lichess",
    "Off topic",
]


class UBlogPost:
    def __init__(self, uid: str):
        self._id = gen.nextId(UBlogPost)
        self.blog = f"user:{uid}"
        self.title = gen.randomTopic()
        self.intro = gen.randomTopic()
        self.markdown = (
            f"![image]({gen.randomImageLink()})\n{gen.randomParagraph()}\n"
            f"![image]({gen.randomImageLink()})\n{gen.randomParagraph()}\n"
            f"![image]({gen.randomImageLink()})\n{gen.randomParagraph()}"
        )
        self.language = "en-US"
        self.live = True
        self.topics = random.sample(_blogTopics, 3)
        self.created = {"by": uid, "at": util.timeSinceDaysAgo(365)}
        self.lived = self.created
        self.updated = self.created
        self.rank = self.created["at"] - timedelta(days=30)  # wtf is this?
        self.views = rrange(10, 100)
        self.likes = rrange(3, 10)
        self.likers = random.sample(gen.uids, self.likes)
