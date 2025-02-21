from modules.env import env
import modules.util as util
import json


def update_local_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.local_bot.drop()
        db.local_asset.drop()

    if args.no_create:
        return

    util.bulk_write(db.local_bot, _read_json("local.bots.json"))
    util.bulk_write(db.local_asset, _read_json("local.assets.json"))

def _read_json(file: str) -> list:
    with open(f"{env.data_path}/{file}", encoding='utf-8') as f:
        return json.load(f)
