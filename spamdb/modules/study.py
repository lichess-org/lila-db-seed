from modules.env import env
import modules.util as util


def update_study_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.study.drop()
        db.study_chapter_flat.drop()
        db.flag.drop()

    study: list[Study] = []
    for bson_study in env.practice_studies:
        s = Study(bson_study)
        study.append(s)

    if not args.no_create:
        util.bulk_write(db.study, study)
        util.bulk_write(db.study_chapter_flat, env.practice_chapters)
        util.bulk_write(db.flag, [{"_id": "practice", "config": env.practice_config}]);
    return study

class Study:
    def __init__(self, study: dict):
        self._id = study["_id"]
        self.name = study["name"]
        self.members = study["members"]
        self.position = study["position"]
        self.ownerId = study["ownerId"]
        self.visibility = study["visibility"]
        self.settings = study["settings"]
        self.__dict__['from'] = study["from"]
        self.likes = study["likes"]
        self.description = study.get("description")
        self.topics = study.get("topics")
        self.flair = study.get("flair")
        self.createdAt = study["createdAt"]
        self.updatedAt = study["updatedAt"]
