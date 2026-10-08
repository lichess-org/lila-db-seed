import math
import random
from datetime import timedelta
from modules.env import env, uci_char_pair
import modules.util as util


def update_study_colls() -> list:
    args = env.args
    db = env.db

    if args.drop:
        db.study.drop()
        db.study_chapter_flat.drop()
        db.flag.drop()

    studies = [Study(bson_study) for bson_study in env.practice_studies]
    chapters = env.practice_chapters.copy()
    for _ in range(args.studies):
        study = Study()
        games = random.sample(env.study_games, util.rrange(2, 33))
        generated = [Chapter(study, game, order) for order, game in enumerate(games, 1)]
        study.position = generated[0]._id + ' '
        study.updatedAt = max(study.updatedAt, *(chapter.createdAt for chapter in generated))
        studies.append(study)
        chapters.extend(generated)

    if not args.no_create:
        util.bulk_write(db.study, studies)
        util.bulk_write(db.study_chapter_flat, chapters)
        util.bulk_write(db.flag, [{'_id': 'practice', 'config': env.practice_config}])
    return studies


class Study:
    def __init__(self, study: dict | None = None):
        if study is not None:
            self.__dict__.update(study)
            return
        self._id = env.next_id(Study)
        self.ownerId = env.random_uid()
        color = random.choice(['Red', 'Green', 'Blue', 'Yellow', 'Pink', 'Silver', 'Gold', 'White', 'Black'])
        shape = random.choice(['Circle', 'Triangle', 'Square', 'Star', 'Cube', 'Pyramid', 'Diamond', 'Hexagon'])
        self.name = f'{self.ownerId.capitalize()} {color} {shape}'
        self.createdAt = util.time_since_days_ago()
        self.updatedAt = util.time_since(self.createdAt)
        members = random.sample(env.uids, util.rrange(0, min(len(env.uids), 12) + 1))
        self.members = {uid: {'role': random.choice(['r', 'w'])} for uid in members}
        self.members[self.ownerId] = {'role': 'w'}
        self.uids = list(self.members)
        self.visibility = random.choices(['public', 'unlisted', 'private'], weights=[8, 1, 1])[0]
        self.settings = {
            key: random.choice(['everyone', 'member', 'contributor', 'owner', 'nobody'])
            for key in ['computer', 'explorer', 'cloneable', 'shareable', 'chat']
        }
        self.settings.update(sticky=util.chance(0.8), description=True)
        self.__dict__['from'] = 'scratch'
        self.likers = list({self.ownerId, *random.sample(env.uids, util.rrange(0, len(env.uids) + 1))})
        self.likes = len(self.likers)
        self.rank = self.createdAt + timedelta(days=min(self.likes, int(5 * math.log(self.likes) + 1)))
        self.description = env.random_paragraph()
        self.topics = random.sample(_topics, util.rrange(1, 6))
        if util.chance(0.6) and env.flairs:
            self.flair = env.random_flair()


class Chapter:
    def __init__(self, study: Study, game, order: int):
        self._id = env.next_id(Chapter)
        self.studyId = study._id
        self.name = game.headers.get('Event', 'Chapter')[:80]
        self.setup = {'variant': 1, 'orientation': util.chance(0.5), 'fromFen': 'FEN' in game.headers}
        self.root = env.study_roots[game]
        self.tags = [f'{key}:{value}' for key, value in game.headers.items()]
        self.order = order
        self.ownerId = random.choice([uid for uid, member in study.members.items() if member['role'] == 'w'])
        self.createdAt = util.time_shortly_after(study.createdAt)
        self.description = env.random_paragraph()
        position = self.root['_']
        path = ''
        for move in game.mainline():
            path += uci_char_pair(move.move)
            position = self.root.get(path.replace('.', chr(144)).replace('$', chr(145)), position)
        self.denorm = {'fen': position['f']}
        if 'u' in position:
            self.denorm['uci'] = position['u']
            if position['s'].endswith(('+', '#')):
                self.denorm['check'] = position['s'][-1]


_topics = [
    'Opening', 'Middlegame', 'Endgame', 'Tactics', 'Strategy', 'Calculation', 'Checkmate', 'Pawn structure',
    'Attack', 'Defence', 'Sacrifice', 'Master games', 'Rook endgames', 'Bishop pair', 'King safety',
    'Sicilian Defence', 'French Defence', 'Ruy Lopez', "Queen's Gambit", 'Chess history',
]
