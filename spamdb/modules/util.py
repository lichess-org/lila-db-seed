import pymongo
import re
import os
import random
import json
import bson
from datetime import datetime
from random import randrange as rrange
from modules.datasrc import gen


def bulk_write(
    coll, objs, append=False
):  # append is used during bson/json export
    if gen.dump_dir != None:
        if not os.path.isdir(gen.dump_dir):
            os.makedirs(gen.dump_dir, exist_ok=True)
        if not os.path.isdir(gen.dump_dir):
            raise FileNotFoundError(gen.dump_dir)
        ext: str = "bson" if gen.bson_mode else "json"
        outpath: str = os.path.join(gen.dump_dir, f"{coll.name}.{ext}")
        openmode = ("a" if append else "w") + ("b" if gen.bson_mode else "")
        with open(outpath, openmode if gen.bson_mode else "w") as f:
            for o in objs:
                if gen.bson_mode:
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


def normalize_id(name: str) -> str:
    return "-".join(re.sub(r"[^\w\s]", "", name.lower()).split())


def chance(probability: float) -> bool:
    return random.uniform(0, 1) < probability


# return a list of n semi-random ints >= minval which add up to sum
def random_partition(sum: int, n: int, minval: int = 1) -> list[int]:
    if n < 1 or sum < 0 or minval < 0:
        raise ValueError(
            f"invalid arguments:  sum={sum}, n={n}, minval={minval}"
        )
    if n * minval > sum:
        minval = 0
    parts: list[int] = []
    for i in range(1, n):
        partition_size = max(
            minval,
            min(
                sum - (n - i) * minval,
                int(sum * random.triangular(0, 0.6, 1 / n)),
            ),
        )
        parts.append(partition_size)
        sum = sum - partition_size
    parts.append(sum)
    random.shuffle(parts)
    return parts


def days_since_genesis(then: datetime = datetime.now()) -> int:
    return (then - datetime(2010, 1, 1, 0, 0, 0)).days


# time_shortly_after provides a date between then and (then + 4 hrs)
def time_shortly_after(then: datetime) -> datetime:
    mintime = int(then.timestamp())
    maxtime = int(min(datetime.now().timestamp(), mintime + 14400))
    return datetime.fromtimestamp(rrange(mintime, maxtime))


# time_since returns a date between then and now
def time_since(then: datetime) -> datetime:
    mintime = int(then.timestamp())
    maxtime = int(datetime.now().timestamp())
    return datetime.fromtimestamp(rrange(mintime, maxtime))


# time_since_days_ago returns a date between (now - days_ago) and now
def time_since_days_ago(days_ago: int) -> datetime:
    thentime = int(datetime.now().timestamp() - rrange(0, days_ago * 86400))
    return datetime.fromtimestamp(thentime)
