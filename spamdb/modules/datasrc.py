import random
import os
import base64
import bson
from random import randrange as rrange
from datetime import datetime


class DataSrc:
    def __init__(self):
        # data source files are assumed to be at <module_dir>/../data
        self.dataPath: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.uids: list[str] = self._readStrings("uids.txt")
        self.countries: list[str] = self._readStrings("countries.txt")
        self.teams: list[str] = self._readStrings("teams.txt", "\n")
        self.categs: list[str] = self._readStrings("categs.txt", "\n")
        self.topics: list[str] = self._readStrings("topics.txt", "\n")
        self.paragraphs: list[str] = self._readStrings("paragraphs.txt", "\n\n")
        self.socialMediaLinks: list[str] = self._readStrings("socialMediaLinks.txt")
        self.imageLinks: list[str] = self._readStrings("imageLinks.txt")
        self.games: list[dict] = self._readBson("game5.bson")
        self.puzzles: list[dict] = self._readBson("puzzle2_puzzle.bson")
        self.puzzlePaths: list[dict] = self._readBson("puzzle2_path.bson")
        self.bullshitModeGames: list[str] = self._readStrings("games.txt", "\n")
        self.seeds = dict[str, int]()
        self.dumpDir = None
        self.bsonMode = True
        self.fideMap: dict[str, int] = {}  # a hack but it's ok

    def setNumUids(self, numIds: int) -> None:
        self.uids = _genN(numUids, self.uids, "user")

    def setNumTeams(self, numTeams: int) -> None:
        self.teams = _genN(numTeams, self.teams, "team")

    def setJsonDumpMode(self, dir: str) -> None:
        self.dumpDir = dir
        self.bsonMode = False

    def setBsonDumpMode(self, dir: str) -> None:
        self.dumpDir = dir
        self.bsonMode = True

    def randomUid(self) -> str:
        return random.choice(self.uids)

    def randomCateg(self) -> str:
        return random.choice(self.categs)

    def randomTopic(self) -> str:
        return random.choice(self.topics)

    def randomCountry(self) -> str:
        return random.choice(self.countries)

    def randomParagraph(self) -> str:
        return random.choice(self.paragraphs)

    def randomSocialMediaLinks(self) -> list[str]:
        return random.sample(self.socialMediaLinks, rrange(0, 6))

    def randomImageLink(self) -> str:
        return random.choice(self.imageLinks)

    def nextId(self, keyObj, numBytes: int = 6) -> str:  # ids only unique inside a collection
        seed = self.seeds.setdefault(keyObj.__class__.__name__, 1)
        self.seeds[keyObj.__class__.__name__] = seed + 1
        return base64.b64encode(seed.to_bytes(numBytes, "big")).decode("ascii")

    def _genN(num: int, ls: list[str], default: str) -> list[str]:
        if not ls:
            ls = [default]
        nextNum: int = 1
        newList: list[str] = ls.copy()
        while len(newList) < num:
            newList.append([e + str(nextNum) for e in ls])
            nextNum = nextNum + 1
        return list(set(newList))[0:num]  # remove dupes, for example if users.txt had both "u" and "u1"

    def _readStrings(self, name: str, sep: str = None) -> list[str]:
        with open(os.path.join(self.dataPath, name), "r") as f:
            return [s for s in f.read().split(sep) if s != ""]

    def _readBson(self, filename: str) -> list[dict]:
        with open(os.path.join(self.dataPath, filename), "rb") as f:
            return bson.decode_all(f.read())


gen = DataSrc()
