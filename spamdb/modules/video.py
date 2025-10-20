from modules.env import env
import modules.util as util


def update_video_colls():
    args = env.args
    db = env.db

    if args.drop:
        db.video.drop()

    if not args.no_create:
        util.bulk_write(db.video, env.videos)
