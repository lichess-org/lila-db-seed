import pymongo
import re
import os
import random
import json
import bson
from datetime import timedelta, datetime
from modules.seed import env


def bulk_write(
    coll: pymongo.collection.Collection,
    objs: list,
    append: bool = False,
) -> None:
    # append parameter is for bson/json export to forum collections
    if len(objs) < 1:
        return
    if env.dump_dir == None:
        # database mode
        ledger = []
        for o in objs:
            ledger.append(_inupsert(_dict(o)))
        res = coll.bulk_write(ledger).bulk_api_result

        print(_report(coll.name, res))
    else:
        # export mode
        if not os.path.isdir(env.dump_dir):
            os.makedirs(env.dump_dir, exist_ok=True)
        if not os.path.isdir(env.dump_dir):
            raise FileNotFoundError(env.dump_dir)
        ext: str = "bson" if env.bson_mode else "json"
        outpath: str = os.path.join(env.dump_dir, f"{coll.name}.{ext}")
        openmode = ("a" if append else "w") + ("b" if env.bson_mode else "")
        with open(outpath, openmode) as f:
            for o in objs:
                if env.bson_mode:
                    f.write(bson.encode(_dict(o)))
                else:
                    f.write(json.dumps(_dict(o), default=str, indent=4))
        print(f"{coll.name} dumped to {outpath}")


# return a list of n semi-random ints >= minval which add up to sum
def random_partition(sum: int, n: int, minval: int = 1) -> list[int]:
    if n < 1 or sum < 0 or minval < 0:
        raise ValueError(f"invalid arguments:  sum={sum}, n={n}, minval={minval}")
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


# time_shortly_after provides a date between then and (then + 1 hr)
def time_shortly_after(then: datetime) -> datetime:
    mintime = int(then.timestamp())
    maxtime = int(min(datetime.now().timestamp(), mintime + 3600))
    return datetime.fromtimestamp(rrange(mintime, maxtime if maxtime > mintime else mintime + 20))


# time_since returns a date between then and now
def time_since(then: datetime) -> datetime:
    restime = datetime.now()
    if then < restime:
        restime = datetime.fromtimestamp(
            random.uniform(int(then.timestamp()), int(restime.timestamp()))
        )
    return restime


# time_since_days_ago returns a date between (now - days_ago) and now
def time_since_days_ago(days_ago = env.args.days) -> datetime:
    return datetime.now() - timedelta(days=random.uniform(0, days_ago))


def insert_json(db: pymongo.MongoClient, filename: str) -> None:
    with open(filename, "r") as f:
        for (collName, objList) in json.load(f).items():
            bulk_write(db[collName], objList)


def _inupsert(o: object) -> object:
    if env.args.drop or env.args.drop_db:
        return pymongo.InsertOne(o)
    else:
        return pymongo.UpdateOne({"_id": o["_id"]}, {"$set": o}, upsert=True)


def _dict(o: object) -> dict:
    return o.__dict__ if hasattr(o, "__dict__") else o


def _report(coll: str, res: pymongo.results.BulkWriteResult) -> str:
    report = f"{coll}: {{"
    if env.args.drop or env.args.drop_db:
        report += f"Inserted: {res['nInserted']}"
    else:
        report += (
            f"Upserted: {res['nUpserted']}, Matched: {res['nMatched']}, "
            f"Modified: {res['nModified']}"
        )
    if res["writeErrors"]:
        report += f", Errors: {res['writeErrors']}"
    return report + "}"
