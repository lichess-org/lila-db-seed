import random
import os
import base64
import bson
from random import randrange as rrange
from datetime import datetime


class DataSrc:
    def __init__(self):
        # data source files are assumed to be at <module_dir>/../data
        self.data_path: str = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data"
        )
        self.uids: list[str] = self._read_strings("uids.txt")
        self.countries: list[str] = self._read_strings("countries.txt")
        self.teams: list[str] = self._read_strings("teams.txt", "\n")
        self.categs: list[str] = self._read_strings("categs.txt", "\n")
        self.topics: list[str] = self._read_strings("topics.txt", "\n")
        self.paragraphs: list[str] = self._read_strings(
            "paragraphs.txt", "\n\n"
        )
        self.social_media_links: list[str] = self._read_strings(
            "social_media_links.txt"
        )
        self.image_links: list[str] = self._read_strings("image_links.txt")
        self.games: list[dict] = self._read_bson("game5.bson")
        self.puzzles: list[dict] = self._read_bson("puzzle2_puzzle.bson")
        self.puzzle_paths: list[dict] = self._read_bson("puzzle2_path.bson")
        self.bullshit_mode_games: list[str] = self._read_strings(
            "games.txt", "\n"
        )
        self.seeds = dict[str, int]()
        self.dump_dir = None
        self.bson_mode = True
        self.fide_map: dict[str, int] = {}  # a hack but it's ok

    def set_num_uids(self, num_uids: int) -> None:
        self.uids = _genN(num_uids, self.uids, "user")

    def set_num_teams(self, num_teams: int) -> None:
        self.teams = _genN(num_teams, self.teams, "team")

    def set_json_dump_mode(self, dir: str) -> None:
        self.dump_dir = dir
        self.bson_mode = False

    def set_bson_dump_mode(self, dir: str) -> None:
        self.dump_dir = dir
        self.bson_mode = True

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
        return random.sample(self.social_media_links, rrange(0, 6))

    def random_image_link(self) -> str:
        return random.choice(self.image_links)

    def next_id(
        self, key_obj, num_bytes: int = 6
    ) -> str:  # ids only unique inside a collection
        seed = self.seeds.setdefault(key_obj.__class__.__name__, 1)
        self.seeds[key_obj.__class__.__name__] = seed + 1
        return base64.b64encode(seed.to_bytes(num_bytes, "big")).decode(
            "ascii"
        )

    def _genN(num: int, ls: list[str], default: str) -> list[str]:
        if not ls:
            ls = [default]
        next_num: int = 1
        new_list: list[str] = ls.copy()
        while len(new_list) < num:
            new_list.append([e + str(next_num) for e in ls])
            next_num = next_num + 1
        return list(set(new_list))[
            0:num
        ]  # remove dupes, for example if users.txt had both "u" and "u1"

    def _read_strings(self, name: str, sep: str = None) -> list[str]:
        with open(os.path.join(self.data_path, name), "r") as f:
            return [s for s in f.read().split(sep) if s != ""]

    def _read_bson(self, filename: str) -> list[dict]:
        with open(os.path.join(self.data_path, filename), "rb") as f:
            return bson.decode_all(f.read())


gen = DataSrc()