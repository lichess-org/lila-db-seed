import pymongo
import re
import os
import random
import json
import bson
from datetime import datetime
from random import randrange as rrange
from modules.datasrc import gen


def bulkwrite(coll, objs, append=False):  # append is used during bson/json export
    if gen.dumpDir != None:
        if not os.path.isdir(gen.dumpDir):
            os.makedirs(gen.dumpDir, exist_ok=True)
        if not os.path.isdir(gen.dumpDir):
            raise FileNotFoundError(gen.dumpDir)
        ext: str = "bson" if gen.bsonMode else "json"
        outpath: str = os.path.join(gen.dumpDir, f"{coll.name}.{ext}")
        openmode = ("a" if append else "w") + ("b" if gen.bsonMode else "")
        with open(outpath, openmode if gen.bsonMode else "w") as f:
            for o in objs:
                if gen.bsonMode:
                    f.write(bson.encode(o.__dict__))
                else:
                    f.write(json.dumps(o.__dict__, default=str, indent=4))
        print(f"Colleciton {coll.name}: dumped to {outpath}")
    else:
        ledger = []
        for x in objs:
            ledger.append(pymongo.DeleteOne({"_id": x._id}))
            ledger.append(pymongo.InsertOne(x.__dict__))
        res = coll.bulk_write(ledger)
        print(f"Collection {coll.name}: {res.bulk_api_result}")


def normalizeId(name: str) -> str:
    return "-".join(re.sub(r"[^\w\s]", "", name.lower()).split())


def chance(probability: float) -> bool:
    return random.uniform(0, 1) < probability


# return a list of n semi-random ints >= minval which add up to sum
def randomPartition(sum: int, n: int, minval: int = 1) -> list[int]:
    if n < 1 or sum < 0 or minval < 0:
        raise ValueError(f"invalid arguments:  sum={sum}, n={n}, minval={minval}")
    if n * minval > sum:
        minval = 0
    parts: list[int] = []
    for i in range(1, n):
        thisPartitionSize = max(
            minval,
            min(sum - (n - i) * minval, int(sum * random.triangular(0, 0.6, 1 / n))),
        )
        parts.append(thisPartitionSize)
        sum = sum - thisPartitionSize
    parts.append(sum)
    random.shuffle(parts)
    return parts


def daysSinceGenesis(thenDate: datetime = datetime.now()) -> int:
    return (thenDate - datetime(2010, 1, 1, 0, 0, 0)).days


# timeShortlyAfter provides a date between thenDate and thenDate + 4 hrs
def timeShortlyAfter(thenDate: datetime) -> datetime:
    mintime = int(thenDate.timestamp())
    maxtime = int(min(datetime.now().timestamp(), mintime + 14400))
    return datetime.fromtimestamp(rrange(mintime, maxtime))


# timeSince returns a date between thenDate and now
def timeSince(thenDate: datetime) -> datetime:
    mintime = int(thenDate.timestamp())
    maxtime = int(datetime.now().timestamp())
    return datetime.fromtimestamp(rrange(mintime, maxtime))


# timeSinceDaysAgo returns a date between (now - daysAgo) and now
def timeSinceDaysAgo(daysAgo: int) -> datetime:
    thentime = int(datetime.now().timestamp() - rrange(0, daysAgo * 86400))
    return datetime.fromtimestamp(thentime)
