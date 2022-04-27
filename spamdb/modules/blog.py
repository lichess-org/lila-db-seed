import pymongo
import random
from datetime import datetime
from datetime import timedelta
from modules.event import evt
from modules.datasrc import gen
import modules.forum as forum
import modules.util as util


def create_blog_colls(db: pymongo.MongoClient, num_blogs: int) -> None:
    if num_blogs < 1:
        return

    ublogs: list = []
    uposts: list = []
    fposts: list = []
    ftopics: list = []

    categ = forum.Categ("Community Blog Discussions")
    slugCounter = 0

    for (num_posts, uid) in zip(
        util.random_partition(num_blogs, len(gen.uids), 0), gen.uids
    ):
        if num_posts == 0:
            continue
        ublogs.append(UBlog(uid))
        # evt.add_blog()

        for _ in range(num_posts):
            uposts.append(UBlogPost(uid))
            ft = forum.Topic(uposts[-1].title, categ._id)
            ft.slug = f"{ft.slug}-{slugCounter}"
            slugCounter = slugCounter + 1
            ft.createdAt = uposts[-1].created["at"]
            ftopics.append(ft)

            for _ in range(util.rrange(4, 48)):
                fp = forum.Post(gen.random_uid())
                fposts.append(fp)
                ft.correlate_post(fp)
                evt.add_post(fp.userId, fp.createdAt, fp._id, ft._id, ft.name)

        for ft in ftopics:
            categ.add_topic(ft)

    util.bulk_write(db.f_categ, [categ], True)
    util.bulk_write(db.f_topic, ftopics, True)
    util.bulk_write(db.f_post, fposts, True)
    util.bulk_write(db.ublog_blog, ublogs)
    util.bulk_write(db.ublog_post, uposts)


def drop(db: pymongo.MongoClient) -> None:
    db.ublog_blog.drop()
    db.ublog_post.drop()


class UBlog:
    def __init__(self, uid: str):
        self._id = f"user:{uid}"
        self.tier = 2


class UBlogPost:
    def __init__(self, uid: str):
        self._id = gen.next_id(UBlogPost)
        self.blog = f"user:{uid}"
        self.title = gen.random_topic()
        self.intro = gen.random_topic()
        self.markdown = (
            f"![image]({gen.random_image_link()})\n{gen.random_paragraph()}\n"
            f"![image]({gen.random_image_link()})\n{gen.random_paragraph()}\n"
            f"![image]({gen.random_image_link()})\n{gen.random_paragraph()}"
        )
        self.language = "en-US"
        self.live = True
        self.discuss = True
        self.topics = random.sample(_blog_topics, 3)
        self.created = {"by": uid, "at": util.time_since_days_ago(365)}
        self.lived = self.created
        self.updated = self.created
        self.rank = self.created["at"] - timedelta(days=30)  # wtf is this?
        self.views = util.rrange(10, 100)
        self.likes = util.rrange(0, len(gen.uids))
        self.likers = random.sample(gen.uids, self.likes)


_blog_topics: list[str] = [
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
