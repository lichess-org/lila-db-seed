import random
import math
from datetime import datetime
from datetime import timedelta
from modules.event import events
from modules.seed import env
import modules.forum as forum
import modules.util as util


def update_blog_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.ublog_blog.drop()
        db.ublog_post.drop()

    if args.ublog_posts < 1:
        return

    ublogs: list = []
    uposts: list = []
    fposts: list = []
    ftopics: list = []

    categ = forum.Categ("Community Blog Discussions")
    categ.hidden = True

    for num_posts, uid in zip(util.random_partition(args.ublog_posts, len(env.uids), 0), env.uids):
        if num_posts == 0:
            continue
        ublogs.append(UBlog(uid))
        tier = ublogs[-1].tier

        for _ in range(num_posts):
            up = UBlogPost(uid, tier)
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
                events.add_post(fp.userId, fp.createdAt, fp._id, ft._id, ft.name)

        for ft in ftopics:
            categ.add_topic(ft)

    if args.no_create:
        return

    util.bulk_write(db.f_categ, [categ], True)
    util.bulk_write(db.f_topic, ftopics, True)
    util.bulk_write(db.f_post, fposts, True)
    util.bulk_write(db.ublog_blog, ublogs)
    util.bulk_write(db.ublog_post, uposts)


class UBlog:
    def __init__(self, uid: str):
        self._id = f"user:{uid}"
        self.tier = random.choices(range(len(_tier_distributions)), _tier_distributions, k=1)[0]


class UBlogPost:
    def __init__(self, uid: str, tier: int):
        self._id = env.next_id(UBlogPost)
        self.blog = f"user:{uid}"
        self.title = env.random_topic()
        self.intro = env.random_topic()
        self.markdown = (
            f"{env.random_paragraph()}\n{env.random_paragraph()}\n{env.random_paragraph()}"
        )
        self.language = "en-US"
        self.live = True
        self.discuss = True
        self.topics = random.sample(_blog_topics, 3)
        self.created = {"by": uid, "at": util.time_since_days_ago()}
        self.lived = self.created
        self.updated = self.created
        self.views = util.rrange(10, 100)
        self.likes = util.rrange(0, len(env.uids))
        self.likers = random.sample(env.uids, self.likes)
        self.rank = self.created["at"] + timedelta(
            days=_tier_rank_day_bonus[tier], hours=math.sqrt(self.likes) + self.likes / 100
        )


_tier_distributions: list[float] = [0.0, 0.05, 0.5, 0.2, 0.1, 0.05]

_tier_rank_day_bonus: list[int] = [-9999, -90, -30, 0, 10, 15]

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
