from modules.seed import env
import modules.util as util


def update_feed_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.daily_feed.drop()

    posts: list[FeedItem] = []

    for _ in range(60):
        posts.append(FeedItem())

    if args.no_create:
        return

    util.bulk_write(db.daily_feed, posts)


class FeedItem:
    def __init__(self):
        self._id = env.next_id(FeedItem)
        self.content = env.random_topic()
        self.public = util.chance(0.8)
        self.at = util.time_since_days_ago(30)
        if util.chance(0.6):
            self.flair = env.random_flair()
