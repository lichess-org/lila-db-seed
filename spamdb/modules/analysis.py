from modules.env import env
import modules.util as util


def update_analysis_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.eval_cache2.drop()

    if args.no_create:
        return

    util.bulk_write(db.eval_cache2, env.eval_cache)
