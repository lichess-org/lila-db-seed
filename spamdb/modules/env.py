import random
import os
import subprocess
import bson
import requests
import chess
import chess.pgn
import re
import string
from modules.args import parse_args
from pymongo.database import Database
from typing import Any


# files used in Env.__init__ are found in spamdb/data folder
class Env:
    db: Database[Any]

    def __init__(self):
        args = self.args = parse_args()
        self.user_bg_mode = args.user_bg
        self.default_password = str(args.password)
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.data_path: str = os.path.join(parent_path, 'data')
        self.uids: list[str] = []
        self.custom_passwords: dict[str, str] = {}
        self._read_users()
        self.countries: list[str] = self._read_strings('countries.txt')
        self.teams: list[str] = self._read_strings('teams.txt')
        self.team_updates: list[str] = self._read_strings('team_updates.txt')
        self.msgs: list[str] = self._read_strings('msgs.txt')
        self.categs: list[str] = self._read_strings('categs.txt')
        self.topics: list[str] = self._read_strings('topics.txt')
        self.paragraphs: list[str] = self._read_strings('paragraphs.txt')
        self.social_media_links: list[str] = self._read_strings('social_media_links.txt')
        self.bg_image_links: list[str] = self._read_strings('bg_image_links.txt')
        self.flairs: list[str] = self._http_get_list(
            'https://raw.githubusercontent.com/lichess-org/lila/master/public/flair/list.txt'
        )
        self.games: list[dict] = self._read_bson('game5.bson')
        self.puzzles: list[dict] = self._read_bson('puzzle2_puzzle.bson')
        self.puzzle_paths: list[dict] = self._read_bson('puzzle2_path.bson')
        self.practice_studies: list[dict] = self._read_bson('study.bson')
        self.practice_chapters: list[dict] = self._read_bson('study_chapter_flat.bson')
        self.study_games: list[chess.pgn.Game] = []
        if args.studies > 0:
            with open(os.path.join(self.data_path, 'study-chapter-source.pgn'), encoding='utf-8-sig') as source:
                while game := chess.pgn.read_game(source):
                    self.study_games.append(game)
            self.study_games = random.sample(self.study_games, min(200, len(self.study_games)))
        self.study_roots = {game: pgn_root(game) for game in self.study_games}
        self.eval_cache: list[dict] = self._read_bson('eval_cache2.bson')
        with open(os.path.join(self.data_path, 'practice-config.txt'), encoding='utf-8') as f:
            self.practice_config = f.read()
        self.videos: list[dict] = self._read_bson('video.bson')
        self.seeds = dict[str, int]()
        self.dump_dir: str | None = None
        self.bson_mode: bool = True  # False means json mode
        self.hash_cache: dict[str, bytes] = {}
        self.lila_crypt_path = os.path.join(os.path.join(parent_path, 'lila_crypt'), 'lila_crypt.jar')
        if args.su_password is not None:
            for admin in self._get_special_users():
                self.custom_passwords[admin] = args.su_password
        if args.users is not None and args.users > -1:
            self.uids = self._genN(max(args.users, 2), self.uids, 'user')
        if args.teams is not None and args.teams > -1:
            self.teams = self._genN(args.teams, self.teams, 'team')
        if args.games is not None and args.games > -1:
            self.games = self.games[: args.games]
        if args.dump_bson:
            self.dump_dir = args.dump_bson
        elif args.dump_json:
            self.dump_dir = args.dump_json
            self.bson_mode = False

    def stable_rating(self, uid: str) -> int:
        try:
            return 2400 - int(1800 * self.uids.index(uid) / len(self.uids))
        except ValueError:
            return 1500

    def get_password(self, uid: str) -> str:
        return self.custom_passwords.get(uid, self.default_password)

    def get_password_hash(self, uid: str) -> bytes:
        password = self.get_password(uid)
        if password in self.hash_cache:
            return self.hash_cache[password]

        result = subprocess.run(
            ['java', '-jar', self.lila_crypt_path, self.args.secret],
            stdout=subprocess.PIPE,
            input=password.encode('utf-8'),
        ).stdout
        if result[0] != 68 or result[1] != 68:
            raise Exception(f'bad output from {self.lila_crypt_path}')
        hash = result[2:]
        self.hash_cache[password] = hash
        return hash

    def random_uid(self) -> str:
        return random.choice(self.uids)

    def random_categ(self) -> str:
        return random.choice(self.categs)

    def random_topic(self) -> str:
        return random.choice(self.topics)

    def random_country(self) -> str:
        return random.choice(self.countries)

    def random_paragraph(self) -> str:
        return random.choice(self.paragraphs)

    def random_team_update(self) -> str:
        return random.choice(self.team_updates)

    def random_social_media_links(self) -> list[str]:
        return random.sample(self.social_media_links, random.randrange(6))

    def random_bg_image_link(self) -> str:
        return random.choice(self.bg_image_links)

    def random_flair(self) -> str:
        return random.choice(self.flairs)

    # ids only unique per collection
    def next_id(self, key_obj, length: int = 8) -> str:
        seed = self.seeds.setdefault(key_obj.__name__, 1)
        self.seeds[key_obj.__name__] = seed + 1
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        identifier = ''
        while seed:
            seed, digit = divmod(seed, len(alphabet))
            identifier = alphabet[digit] + identifier
        return identifier.rjust(length, 'A')

    def _genN(self, n: int, orig_list: list[str], default: str) -> list[str]:
        if not orig_list:
            orig_list = [default]
        next_suffix: int = 1
        new_list: list[str] = orig_list.copy()
        while len(new_list) < n:
            new_list.extend([e + str(next_suffix) for e in orig_list])
            next_suffix = next_suffix + 1
        return new_list[0:n]

    def _read_strings(self, name: str) -> list[str]:
        with open(os.path.join(self.data_path, name), 'r') as f:
            return [s.strip() for s in f.read().splitlines() if s and not s.lstrip().startswith('#')]

    def _http_get_list(self, url: str) -> list[str]:
        return requests.get(url).text.splitlines()

    def _read_bson(self, filename: str) -> list[dict]:
        with open(os.path.join(self.data_path, filename), 'rb') as f:
            return bson.decode_all(f.read())

    def _get_special_users(self) -> list[str]:
        return (
            [self.args.su]
            if self.args.su
            else [
                'lichess',
                'superadmin',
                'admin',
                'shusher',
                'hunter',
                'puzzler',
            ]
        )

    def _read_users(self) -> None:
        with open(os.path.join(self.data_path, 'uids.txt'), 'r') as f:
            for line in f.read().splitlines():
                entry = line.strip()
                if not entry or entry.startswith('#'):
                    continue
                fields = entry.split('/', 1)
                uid = fields[0].lower().rstrip()
                if uid not in self._get_special_users():
                    self.uids.append(uid)
                if len(fields) > 1:
                    self.custom_passwords[uid] = fields[1].lstrip()


def uci_char_pair(move: chess.Move) -> str:
    destination = move.to_square + 35
    if move.promotion:
        destination = 99 + 'qrbnk'.index(chess.piece_symbol(move.promotion)) * 8 + chess.square_file(move.to_square)
    return chr(move.from_square + 35) + chr(destination)


def pgn_root(game: chess.pgn.Game) -> dict[str, dict]:
    board = game.board()
    root = {'_': {'p': board.ply(), 'f': board.fen(en_passant='fen'), **pgn_annotations(game)}}
    pending = [(child, board.copy(stack=False), '', 1) for child in reversed(game.variations)]
    while pending and len(root) <= 3000:
        node, board, parent, depth = pending.pop()
        move = node.move
        path = parent + uci_char_pair(move)
        san = board.san(move)
        board.push(move)
        root[path.replace('.', chr(144)).replace('$', chr(145))] = {
            'p': board.ply(),
            'u': move.uci(),
            's': san,
            'f': board.fen(en_passant='fen'),
            **pgn_annotations(node),
        }
        if depth < 600:
            pending.extend((child, board.copy(stack=False), path, depth + 1) for child in reversed(node.variations))
    return root


def pgn_annotations(node: chess.pgn.GameNode) -> dict:
    annotations: dict = {}
    text = re.sub(r'\[%[^\]]+\]', '', '\n'.join(filter(None, [node.starting_comment, node.comment]))).strip()
    if text:
        annotations['co'] = [{
            'id': ''.join(random.choices(string.ascii_letters + string.digits, k=4)),
            'text': text[:4000],
            'by': '',
        }]
    if node.nags:
        annotations['g'] = sorted(node.nags)
    shapes = []
    for arrow in node.arrows():
        if arrow.tail == arrow.head:
            shapes.append({'b': arrow.color, 'p': chess.square_name(arrow.tail)})
        else:
            shapes.append({'b': arrow.color, 'o': chess.square_name(arrow.tail), 'd': chess.square_name(arrow.head)})
    if shapes:
        annotations['h'] = shapes
    clock = node.clock()
    if clock is not None:
        annotations['l'] = round(clock * 100)
    score = node.eval()
    if score is not None:
        white = score.white()
        mate = white.mate()
        if mate is None:
            annotations['e'] = max(-999999, min(999999, white.score()))
        elif mate == 0:
            annotations['e'] = 2147483647 if white == chess.engine.MateGiven else -2147483648
        else:
            annotations['e'] = mate * 1000000
    return annotations


env = Env()  # used by other modules
