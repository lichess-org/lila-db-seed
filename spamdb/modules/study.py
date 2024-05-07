from modules.env import env
import modules.util as util


def update_study_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.study.drop()
        db.study_chapter_flat.drop()
        db.flag.drop()

    if not args.no_create:
        util.bulk_write(db.study, env.practice_studies)
        util.bulk_write(db.study_chapter_flat, env.practice_chapters)
        util.bulk_write(db.flag, [{"_id": "practice", "config": env.practice_config}]);
    return []
