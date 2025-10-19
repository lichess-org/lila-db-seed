from modules.env import env
import modules.util as util
import json


def update_jsbot_colls() -> None:
    args = env.args
    db = env.db

    if not args.jsbots:
        return

    if args.drop:
        db.jsbot.drop()
        db.jsbot_asset.drop()

    if args.no_create:
        return

    util.bulk_write(db.jsbot, _read_json('jsbot.json'))
    util.bulk_write(db.jsbot_asset, _read_json('jsbot.asset.json'))


def _read_json(file: str) -> list:
    with open(f'{env.data_path}/{file}', encoding='utf-8') as f:
        return json.load(f)
