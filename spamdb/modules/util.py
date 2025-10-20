from pymongo import collection, results, InsertOne, UpdateOne
import re
import os
import random
import json
import bson
from datetime import timedelta, datetime
from modules.env import env
from typing import Any, Mapping


def bulk_write(
    coll: collection.Collection,
    objs: list[Any],
    append: bool = False,
) -> None:
    # append parameter is for bson/json export to forum collections
    if len(objs) == 0:
        return
    if env.dump_dir is None:
        # database mode
        ledger = []
        for o in objs:
            ledger.append(_inupsert(_dict(o)))
        res = coll.bulk_write(ledger)

        print(_report(coll.name, res))
    else:
        # export mode
        if not os.path.isdir(env.dump_dir):
            os.makedirs(env.dump_dir, exist_ok=True)
        if not os.path.isdir(env.dump_dir):
            raise FileNotFoundError(env.dump_dir)
        ext: str = 'bson' if env.bson_mode else 'json'
        outpath: str = os.path.join(env.dump_dir, f'{coll.name}.{ext}')
        openmode = ('a' if append else 'w') + ('b' if env.bson_mode else '')
        with open(outpath, openmode) as f:
            for o in objs:
                if env.bson_mode:
                    f.write(bson.encode(_dict(o)))
                else:
                    f.write(json.dumps(_dict(o), default=str, indent=4))
        print(f'{coll.name} dumped to {outpath}')


# return a list of n semi-random ints >= minval which add up to sum
def random_partition(sum: int, n: int, minval: int = 1) -> list[int]:
    if n < 1 or sum < 0 or minval < 0:
        raise ValueError(f'invalid arguments:  sum={sum}, n={n}, minval={minval}')
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
    return '-'.join(re.sub(r'[^\w\s]', '', name.lower()).split())


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
        restime = datetime.fromtimestamp(random.uniform(int(then.timestamp()), int(restime.timestamp())))
    return restime


# time_since_days_ago returns a date between (now - days_ago) and now
def time_since_days_ago(days_ago=env.args.days) -> datetime:
    return datetime.now() - timedelta(days=random.uniform(0, days_ago))


def _inupsert(o: object) -> object:
    if env.args.drop or env.args.drop_db:
        return InsertOne(_dict(o))
    else:
        return UpdateOne({'_id': _dict(o)['_id']}, {'$set': o}, upsert=True)


def _dict(o: Any) -> dict[str, Any]:
    if isinstance(o, dict):
        return o
    if hasattr(o, '__dict__'):
        return vars(o)
    if isinstance(o, Mapping):
        return dict(o)
    raise TypeError('not a dict')


def _report(coll: str, res: results.BulkWriteResult) -> str:
    report = f'{coll.ljust(24, ".")} '
    if env.args.drop or env.args.drop_db:
        report += f'Inserted: {res.inserted_count}'
    else:
        report += f'Upserted: {str(res.upserted_count).ljust(6, " ")}'
        report += f'Matched: {str(res.matched_count).ljust(7, " ")}'
        report += f'Modified: {res.modified_count}'
    if res.bulk_api_result['writeErrors']:
        report += f', Errors: {res.bulk_api_result["writeErrors"]}'
    return report
