import pymongo
import random
import argparse
from datetime import datetime
from datetime import timedelta
from modules.event import events
from modules.seed import env
import modules.forum as forum
import modules.util as util


def update_blog_colls() -> None:
    args = env.args
    db = env.db
    do_drop = args.drop == "blog" or args.drop == "all"

    if do_drop:
        db.ublog_blog.drop()
        db.ublog_post.drop()

    if args.blogs < 1:
        return

    ublogs: list = []
    uposts: list = []
    fposts: list = []
    ftopics: list = []

    categ = forum.Categ("Community Blog Discussions")
    categ.hidden = True

    for (num_posts, uid) in zip(
        util.random_partition(args.blogs, len(env.uids), 0), env.uids
    ):
        if num_posts == 0:
            continue
        ublogs.append(UBlog(uid))

        for _ in range(num_posts):
            up = UBlogPost(uid)
            uposts.append(up)
            up.slug = util.normalize_id(up.title)
            ft = forum.Topic(up.title, categ._id)
            ft.userId = uid
            ft.slug = f"ublog-{uid}-{up._id}"
            ft.createdAt = uposts[-1].created["at"]
            ft.blogUrl = f"/@/{uid}/blog/{up.slug}/{up._id}"
            fpost = forum.Post(uid)  # welcome post
            fpost.text = "Discussing: " + ft.blogUrl
            ft.correlate_post(fpost)
            fposts.append(fpost)
            ftopics.append(ft)

            for _ in range(util.rrange(2, 8)):
                fp = forum.Post(env.random_uid())
                fposts.append(fp)
                ft.correlate_post(fp)
                events.add_post(
                    fp.userId, fp.createdAt, fp._id, ft._id, ft.name
                )

        for ft in ftopics:
            categ.add_topic(ft)

    if args.no_create:
        return

    util.bulk_write(db.f_categ, [categ], do_drop, True)
    util.bulk_write(db.f_topic, ftopics, do_drop, True)
    util.bulk_write(db.f_post, fposts, do_drop, True)
    util.bulk_write(db.ublog_blog, ublogs, do_drop)
    util.bulk_write(db.ublog_post, uposts, do_drop)


class UBlog:
    def __init__(self, uid: str):
        self._id = f"user:{uid}"
        self.tier = 2


class UBlogPost:
    def __init__(self, uid: str):
        self._id = env.next_id(UBlogPost)
        self.blog = f"user:{uid}"
        self.title = env.random_topic()
        self.intro = env.random_topic()
        self.markdown = (
            f"![image]({env.random_image_link()})\n{env.random_paragraph()}\n"
            f"![image]({env.random_image_link()})\n{env.random_paragraph()}\n"
            f"![image]({env.random_image_link()})\n{env.random_paragraph()}"
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
        self.likes = util.rrange(0, len(env.uids))
        self.likers = random.sample(env.uids, self.likes)


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
