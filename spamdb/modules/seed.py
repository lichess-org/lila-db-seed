import random
import os
import subprocess
import base64
import bson
import argparse
import modules.util as util
from modules.args import parse_args

# files used in seed.__init__ are found in spamdb/data folder
class Seed:
    def __init__(self):
        args = self.args = parse_args()
        self.user_bg_mode = args.user_bg
        self.default_password = args.password
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.data_path: str = os.path.join(parent_path, "data")
        self.uids: list[str] = []
        self.custom_passwords: dict[str, str] = {}
        self._read_users()
        self.countries: list[str] = self._read_strings("countries.txt")
        self.teams: list[str] = self._read_strings("teams.txt")
        self.msgs: list[str] = self._read_strings("msgs.txt")
        self.categs: list[str] = self._read_strings("categs.txt")
        self.topics: list[str] = self._read_strings("topics.txt")
        self.paragraphs: list[str] = self._read_strings("paragraphs.txt")
        self.social_media_links: list[str] = self._read_strings("social_media_links.txt")
        self.bg_image_links: list[str] = self._read_strings("bg_image_links.txt")
        self.games: list[dict] = self._read_bson("game5.bson")
        self.puzzles: list[dict] = self._read_bson("puzzle2_puzzle.bson")
        self.puzzle_paths: list[dict] = self._read_bson("puzzle2_path.bson")
        self.seeds = dict[str, int]()
        self.dump_dir: str = None
        self.bson_mode: bool = True  # False means json mode
        self.fide_map: dict[str, int] = {}
        self.hash_cache: dict[str, int] = {}
        self.lila_crypt_path = os.path.join(
            os.path.join(parent_path, "lila_crypt"), "lila_crypt.jar"
        )
        if args.su_password is not None:
            for admin in self._special_users:
                self.custom_passwords[admin] = args.su_password
        if args.users is not None and args.users > -1:
            self.uids = self._genN(max(args.users, 2), self.uids, "user")
        if args.teams is not None and args.teams > -1:
            self.teams = self._genN(args.teams, self.teams, "team")
        if args.games is not None and args.games > -1:
            self.games = self.games[: args.games]
        if args.dump_bson:
            self.dump_dir = args.dump_bson
        elif args.dump_json:
            self.dump_dir = args.dump_json
            self.bson_mode = False


    def get_password_hash(self, uid: str) -> bytes:
        password = self.custom_passwords.get(uid, self.default_password)
        if password in self.hash_cache:
            return self.hash_cache[password]

        result = subprocess.run(
            ["java", "-jar", self.lila_crypt_path, self.args.secret],
            stdout=subprocess.PIPE,
            input=password.encode("utf-8"),
        ).stdout
        if result[0] != 68 or result[1] != 68:
            raise Exception(f"bad output from {self.lila_crypt_path}")
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

    def random_social_media_links(self) -> list[str]:
        return random.sample(self.social_media_links, util.rrange(0, 6))

    def random_bg_image_link(self) -> str:
        return random.choice(self.bg_image_links)

    # ids only unique per collection
    def next_id(self, key_obj, num_bytes: int = 6) -> str:
        seed = self.seeds.setdefault(key_obj.__name__, 1)
        self.seeds[key_obj.__name__] = seed + 1
        return base64.b64encode(seed.to_bytes(num_bytes, "big")).decode("ascii")

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
        with open(os.path.join(self.data_path, name), "r") as f:
            return [
                s.strip() for s in f.read().splitlines() if s and not s.lstrip().startswith("#")
            ]

    def _read_bson(self, filename: str) -> list[dict]:
        with open(os.path.join(self.data_path, filename), "rb") as f:
            return bson.decode_all(f.read())

    _special_users: list[str] = [
        "lichess",
        "superadmin",
        "admin",
        "shusher",
        "hunter",
        "puzzler",
        "api",
    ]

    def _read_users(self) -> None:
        with open(os.path.join(self.data_path, "uids.txt"), "r") as f:
            for line in f.read().splitlines():
                entry = line.strip()
                if not entry or entry.startswith("#"):
                    continue
                fields = entry.split("/", 1)
                uid = fields[0].lower().rstrip()
                if uid not in self._special_users:
                    self.uids.append(uid)
                if len(fields) > 1:
                    self.custom_passwords[uid] = fields[1].lstrip()


env = Seed()  # used by other modules
