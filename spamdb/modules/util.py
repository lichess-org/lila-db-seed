import pymongo
import re
import os
import random
import json
import bson
from datetime import timedelta
from datetime import datetime
from modules.datasrc import gen


def bulk_write(coll, objs, append=False):
    # append parameter is used during bson/json export
    if len(objs) < 1:
        return
    if gen.dump_dir != None:
        if not os.path.isdir(gen.dump_dir):
            os.makedirs(gen.dump_dir, exist_ok=True)
        if not os.path.isdir(gen.dump_dir):
            raise FileNotFoundError(gen.dump_dir)
        ext: str = "bson" if gen.bson_mode else "json"
        outpath: str = os.path.join(gen.dump_dir, f"{coll.name}.{ext}")
        openmode = ("a" if append else "w") + ("b" if gen.bson_mode else "")
        with open(outpath, openmode) as f:
            for o in objs:
                if gen.bson_mode:
                    f.write(bson.encode(_dict(o)))
                else:
                    f.write(json.dumps(_dict(o), default=str, indent=4))
        print(f"Collection {coll.name}: dumped to {outpath}")
    else:
        ledger = []
        for x in objs:
            ledger.append(pymongo.DeleteOne({"_id": _dict(x)["_id"]}))
            ledger.append(pymongo.InsertOne(_dict(x)))
        res = coll.bulk_write(ledger)
        print(f"Collection {coll.name}: {res.bulk_api_result}")


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


# random.range exceptions are helpful and all but we don't want them
# in many procedural generation boundary conditions
def rrange(lower: int, upper: int) -> int:
    if upper <= lower:
        return upper
    else:
        return random.randrange(lower, upper)


def normalize_id(name: str) -> str:
    return "-".join(re.sub(r"[^\w\s]", "", name.lower()).split())


def chance(probability: float) -> bool:
    return random.uniform(0, 1) < probability


def days_since_genesis(then: datetime = datetime.now()) -> int:
    return (then - datetime(2010, 1, 1, 0, 0, 0)).days


# time_shortly_after provides a date between then and (then + 4 hrs)
def time_shortly_after(then: datetime) -> datetime:
    mintime = int(then.timestamp())
    maxtime = int(min(datetime.now().timestamp(), mintime + 14400))
    return datetime.fromtimestamp(
        rrange(mintime, maxtime if maxtime > mintime else mintime + 20)
    )


# time_since returns a date between then and now
def time_since(then: datetime) -> datetime:
    restime = datetime.now()
    if then < restime:
        restime = datetime.fromtimestamp(
            random.uniform(int(then.timestamp()), int(restime.timestamp()))
        )
    return restime


# time_since_days_ago returns a date between (now - days_ago) and now
def time_since_days_ago(days_ago: int) -> datetime:
    return datetime.now() - timedelta(days=random.uniform(0, days_ago))


def insert_json(db: pymongo.MongoClient, filename: str) -> None:
    with open(filename, "r") as f:
        for (collName, objList) in json.load(f).items():
            bulk_write(db[collName], objList)


def _dict(o: object) -> dict:
    return o.__dict__ if hasattr(o, "__dict__") else o
