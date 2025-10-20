import random
from datetime import datetime, timedelta
from modules.event import events
from modules.env import env
import modules.util as util


def update_forum_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.f_categ.drop()
        db.f_topic.drop()
        db.f_post.drop()

    if args.forum_posts < 1:
        return []

    categs: dict[str, Categ] = {}
    topics: list[Topic] = []
    posts: list[Post] = []

    for cat_name in env.categs:
        categ = Categ(cat_name)
        categs[categ._id] = categ

    while len(topics) < args.forum_posts / 8:
        for topic_name in env.topics:
            iter = int(len(topics) / len(env.topics))
            topics.append(
                Topic(
                    topic_name if iter == 0 else f'{topic_name} {iter}',
                    random.choice(list(categs.keys())),
                )
            )

    for _ in range(args.forum_posts):
        p = Post(env.random_uid())
        posts.append(p)
        t = random.choice(topics)
        t.correlate_post(p)
        events.add_post(p.userId, p.createdAt, p._id, t._id, t.name)

    for t in topics:
        if hasattr(t, 'lastPostId'):
            categs[t.categId].add_topic(t)

    diagnostic = Categ('Diagnostic', False, 'User diagnostic reports')
    diagnostic.hidden = True
    diagnostic.quiet = True
    categs[diagnostic._id] = diagnostic
    headerPost = Post('admin')
    headerPost.text = 'none'
    headerTopic = Topic('none', diagnostic._id)
    headerTopic.correlate_post(headerPost)
    diagnostic.add_topic(headerTopic)

    if not args.no_create:
        util.bulk_write(db.f_categ, list(categs.values()))
        util.bulk_write(db.f_topic, topics)
        util.bulk_write(db.f_post, posts)
    return posts


class Post:
    topicId: str
    categId: str
    number: int
    topic: str

    def __init__(self, uid: str):
        self._id = env.next_id(Post)
        self.text = env.random_paragraph()
        self.troll = False
        self.hidden = False
        self.createdAt = datetime.now()
        self.userId = uid


class Topic:
    blogUrl: str

    def __init__(self, name: str, categ_id: str):
        self._id = env.next_id(Topic)
        self.name = name
        self.slug = util.normalize_id(name)
        self.categId = categ_id
        self.createdAt = util.time_since_days_ago() - timedelta(days=2)
        self.updatedAt = self.updatedAtTroll = self.createdAt
        self.nbPosts = self.nbPostsTroll = 0
        self.troll = False
        self.hidden = False
        self.closed = util.chance(0.1)
        self.userId = env.random_uid()

    # keep the refs and sequencing fields consistent
    def correlate_post(self, p: Post):
        self.lastPostId = self.lastPostIdTroll = p._id
        self.updatedAt = self.updatedAtTroll = p.createdAt = util.time_shortly_after(self.updatedAt)
        self.nbPosts = self.nbPostsTroll = self.nbPosts + 1
        p.topicId = self._id
        p.categId = self.categId
        p.number = self.nbPosts
        p.topic = self.name  # for search.py, otherwise unused


class Categ:
    def __init__(self, name: str, team: bool = False, desc: str = env.random_topic()):
        self._id = ('team-' if team else '') + util.normalize_id(name)
        self.name = name
        self.desc = desc
        self.nbTopics = 0
        self.nbPosts = 0
        self.nbTopicsTroll = 0
        self.nbPostsTroll = 0
        self.quiet = False
        self.hidden = False
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
