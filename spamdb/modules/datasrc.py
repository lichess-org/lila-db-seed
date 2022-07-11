import random
import os
import subprocess
import base64
import bson
import modules.util as util
from datetime import datetime

# filenames used in DataSrc.__init__ are REQUIRED to be in <spamdb-path>/data
class DataSrc:
    def __init__(self):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.data_path: str = os.path.join(parent_path, "data")
        self.uids: list[str] = []
        self.custom_pwds: dict[str, str] = {}
        self._read_users()
        self.countries: list[str] = self._read_strings("countries.txt")
        self.teams: list[str] = self._read_strings("teams.txt")
        self.categs: list[str] = self._read_strings("categs.txt")
        self.topics: list[str] = self._read_strings("topics.txt")
        self.paragraphs: list[str] = self._read_strings("paragraphs.txt")
        self.social_media_links: list[str] = self._read_strings(
            "social_media_links.txt"
        )
        self.image_links: list[str] = self._read_strings("image_links.txt")
        self.games: list[dict] = self._read_bson("game5.bson")
        self.puzzles: list[dict] = self._read_bson("puzzle2_puzzle.bson")
        self.puzzle_paths: list[dict] = self._read_bson("puzzle2_path.bson")
        self.seeds = dict[str, int]()
        self.dump_dir: str = None
        self.bson_mode: bool = True
        self.user_bg_mode: int = 200
        self.fide_map: dict[str, int] = {}
        self.default_password = "password"
        self.lila_crypt_path = os.path.join(
            os.path.join(parent_path, "lila_crypt"), "lila_crypt.jar"
        )
        self.hash_cache: dict[str, int] = {
            "password": base64.b64decode(
                "E11iacfUn7SA1X4pFDRi+KkX8kT2XnckW6kx+w5AY7uJet8q9mGv"
            ),
        }

    def set_num_uids(self, num_uids: int) -> None:
        if num_uids < 2:
            num_uids = 2  # can't have less than 2 normal users because reasons
        self.uids = self._genN(num_uids, self.uids, "user")

    def set_num_teams(self, num_teams: int) -> None:
        self.teams = self._genN(num_teams, self.teams, "team")

    def set_json_dump_mode(self, dir: str) -> None:
        self.dump_dir = dir
        self.bson_mode = False

    def set_bson_dump_mode(self, dir: str) -> None:
        self.dump_dir = dir
        self.bson_mode = True

    # used to round trip with unique salt for each user for customized passwords,
    # but apparently this could take many minutes for just 80'ish users for devs
    # with slow pcs due to both context switching in the tight loop and bcrypt
    # rounds.  unique salt really not necessary here so there's no need to batch,
    # this here should be fast enough.

    def get_password_hash(self, uid: str) -> bytes:
        password = self.custom_pwds.get(uid, self.default_password)
        if password in self.hash_cache:
            return self.hash_cache[password]

        result = subprocess.run(
            ["java", "-jar", self.lila_crypt_path],
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

    def random_image_link(self) -> str:
        return random.choice(self.image_links)

    # ids only unique per collection
    def next_id(self, key_obj, num_bytes: int = 6) -> str:
        seed = self.seeds.setdefault(key_obj.__name__, 1)
        self.seeds[key_obj.__name__] = seed + 1
        return base64.b64encode(seed.to_bytes(num_bytes, "big")).decode(
            "ascii"
        )

    def _genN(self, num: int, ls: list[str], default: str) -> list[str]:
        if num == 0:
            return []
        if not ls:
            ls = [default]
        next_num: int = 1
        new_list: list[str] = ls.copy()
        while len(new_list) < num:
            new_list.extend([e + str(next_num) for e in ls])
            next_num = next_num + 1
        return new_list[0:num]

    def _read_strings(self, name: str) -> list[str]:
        with open(os.path.join(self.data_path, name), "r") as f:
            return [
                s.strip()
                for s in f.read().splitlines()
                if s and not s.lstrip().startswith("#")
            ]

    def _read_bson(self, filename: str) -> list[dict]:
        with open(os.path.join(self.data_path, filename), "rb") as f:
            return bson.decode_all(f.read())

    _special_users: list[str] = [
        "lichess",
        "admin",
        "shusher",
        "hunter",
        "puzzler",
        "api",
    ]

    def _read_users(self) -> None:
        with open(os.path.join(self.data_path, "uids.txt"), "r") as f:
            for line in f.read().splitlines():
                if line.lstrip().startswith("#"):
                    continue
                bits = line.strip().split("/", 1)
                uid = bits[0].lower()
                if uid not in self._special_users:
                    self.uids.append(uid)
                if len(bits) == 2:
                    self.custom_pwds[uid] = bits[1]


gen = DataSrc()  # used by other modules
