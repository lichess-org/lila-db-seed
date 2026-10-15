import math
import random
from datetime import timedelta
from modules.env import env, uci_char_pair
import modules.util as util


def update_study_colls() -> list:
    args = env.args
    db = env.db

    if args.drop or args.studies > 0:
        db.study.drop()
        db.study_chapter_flat.drop()
    if args.drop:
        db.flag.drop()

    studies = [Study(bson_study) for bson_study in env.practice_studies]
    chapters = env.practice_chapters.copy()
    reversed_uids = list(reversed(env.uids))
    append = False

    for n in range(args.studies):
        uids = reversed_uids
        if args.studies > 1000:
            # for big study-db testing - user study memberships grow according to their position in uids.txt
            # patricia, adriana, kenneth, and abubakar love studies
            min_slice = min(8, len(uids))
            user_slice_end = min_slice + round(n * (len(uids) - min_slice) / args.studies)
            uids = uids[:user_slice_end]
        study = Study(None, uids)

        # chapter counts curve so most studies will have 4-10 chapters with occasional bigguns
        game_count = max(2, min(64, math.ceil(random.gammavariate(2, 4))))
        games = random.sample(env.study_games, game_count)
        generated = [Chapter(study, game, order) for order, game in enumerate(games, 1)]
        study.position = generated[0]._id + ' '
        study.updatedAt = max(study.updatedAt, *(chapter.createdAt for chapter in generated))
        studies.append(study)
        chapters.extend(generated)

        if len(chapters) >= 10_000:
            # when making millions of studies, chapter storage grows large. flush and clear occasionally
            if not args.no_create:
                util.bulk_write(db.study_chapter_flat, chapters, append)
                append = True
            chapters.clear()

    if not args.no_create:
        util.bulk_write(db.study, studies)
        util.bulk_write(db.study_chapter_flat, chapters, append)
        util.bulk_write(db.flag, [{'_id': 'practice', 'config': env.practice_config}])
    return studies


class Study:
    def __init__(self, study: dict | None, uids: list[str] | None = env.uids):
        if study is not None:
            self.__dict__.update(study)
            return
        self._id = env.next_id(Study)
        self.ownerId = random.choice(uids)
        color = random.choice(
            [
                'Red',
                'Green',
                'Blue',
                'Yellow',
                'Pink',
                'Silver',
                'Gold',
                'White',
                'Black',
                'Orange',
                'Purple',
                'Brown',
                'Cyan',
                'Magenta',
                'Turquoise',
                'Beige',
                'Lavender',
                'Maroon',
                'Olive',
                'Coral',
                'Navy',
                'Teal',
                'Lime',
                'Indigo',
                'Violet',
                'Aquamarine',
                'Chartreuse',
                'Fuchsia',
                'Khaki',
                'Plum',
                'Salmon',
                'Tan',
                'Tomato',
                'Wheat',
                'Copper',
                'Bronze',
                'Ruby',
                'Emerald',
                'Sapphire',
                'Amethyst',
                'Topaz',
                'Opal',
                'Pearl',
                'Onyx',
                'Jade',
                'Garnet',
                'Peridot',
                'Spinel',
                'Tourmaline',
                'Zircon',
                'Mauve',
                'Cerulean',
                'Amber',
                'Crimson',
                'Emerald',
                'Ivory',
                'Jade',
                'Lilac',
                'Magenta',
                'Ochre',
                'Periwinkle',
                'Rose',
                'Saffron',
                'Scarlet',
                'Sepia',
                'Turquoise',
                'Ultramarine',
                'Viridian',
                'Zaffre',
            ]
        )
        shape = random.choice(
            [
                'Circle',
                'Triangle',
                'Square',
                'Star',
                'Cube',
                'Pyramid',
                'Diamond',
                'Hexagon',
                'Tertagon',
                'Tetrahedron',
                'Dodecahedron',
                'Icosahedron',
                'Octahedron',
                'Heptagon',
                'Nonagon',
                'Enneagon',
                'Decagon',
                'Hendecagon',
                'Duodecagon',
                'Tridecagon',
                'Tetradecagon',
                'Pentadecagon',
                'Hexadecagon',
                'Heptadecagon',
                'Octadecagon',
                'Enneadecagon',
                'Torus',
                'Sphere',
                'Cylinder',
                'Cone',
                'Prism',
                'Frustum',
                'Manifold',
                'Hypercube',
                'Tesseract',
                'Ellipsoid',
                'Mobius Strip',
                'Klein Bottle',
                'Parallelepiped',
                'Ring',
                'Knot',
                'Plane',
                'Hyperboloid',
                'Paraboloid',
                'Capsule',
                'Prismatoid',
                'Octagram',
                'Nonagram',
            ]
        )
        self.name = f'{self.ownerId.capitalize()} {color} {shape}'
        self.createdAt = util.time_since_days_ago()
        self.updatedAt = util.time_since(self.createdAt)
        members = random.sample(uids, util.rrange(0, min(len(uids), 4) + 1))
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
        if util.chance(0.3):
            self.description = env.random_topic()
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
        if util.chance(0.2):
            self.description = env.random_topic()
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
    'Opening',
    'Middlegame',
    'Endgame',
    'Tactics',
    'Strategy',
    'Calculation',
    'Checkmate',
    'Pawn structure',
    'Attack',
    'Defence',
    'Sacrifice',
    'Master games',
    'Rook endgames',
    'Bishop pair',
    'King safety',
    'Sicilian Defence',
    'French Defence',
    'Ruy Lopez',
    "Queen's Gambit",
    'Chess history',
]
