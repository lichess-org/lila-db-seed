# Database data for development on lichess-org/lila

> [!NOTE]
> If you use [lila-gitpod](https://github.com/lichess-org/lila-gitpod) or [lila-docker](https://github.com/lichess-org/lila-docker) for your dev environment, this repo is already included and you can configure it during setup.

### This will get you the bare minimum of puzzles and game data:

```bash
mongorestore dump
```

# Or...

### Use spamdb to fully populate your database:

[python3.9+](https://www.python.org/) is required. If you don't have python3, use your package manager or the [downloads page](https://www.python.org/downloads/) to install it, then install the necessary packages:

```sh
python -m ensurepip --upgrade
# not strictly necessary but recommended, use a virtual environment
python3 -m venv venv --upgrade-deps && source venv/bin/activate
# install required packages
pip3 install -r spamdb/requirements.txt
```

The `lila-db-seed/spamdb/spamdb.py` script will generate semi-realistic dummy data that is useful for testing and makes your dev instance a lot more colorful. Usage help:

```bash
spamdb/spamdb.py --help
```

Usually, the script will generate a new set of data from inputs in the provided arguments as well as the `spamdb/data` directory. This data will be merged into your running mongodb instance at `127.0.0.1:27071/lichess` by default. To customize connection details use the `--uri` argument. Set the password for your users with the `--password` flag (otherwise they will default to "password"). Set the default background in user prefs with `--user-bg` (default is dark mode, use 400 for transparency). For other options see `spamdb.py --help`.

### Use `--su-password` to give the special (admin) users different passwords than the default if your dev instance will be exposed to others.

### Creating lichess database indexes

`lila-db-seed/spamdb/spamdb.py` does not create the indexes in lichess database. In case you need them, you can use https://github.com/lichess-org/lila/blob/master/bin/mongodb/indexes.js

```bash
mongosh --quiet lichess indexes.js
```

## Seed Elasticsearch

To push this data to elasticsearch, you can use the CLI tools from [lila-search](https://github.com/lichess-org/lila-search). See the CLI commands in the [lila-search README](https://github.com/lichess-org/lila-search?tab=readme-ov-file#cli-tool).

## Special users:

-   superadmin - ROLE_SUPER_ADMIN # check out the mod UI if you haven't seen it, very cool!
-   admin - ROLE_ADMIN
-   shusher - ROLE_SHUSHER
-   hunter - ROLE_CHEAT_HUNTER
-   puzzler - ROLE_PUZZLE_CURATOR
-   api - ROLE_API_HOG (this guy is useful for api testing, both server and clients)
-   troll - marked as troll
-   bot0 thru bot9 - marked as bot
-   kid - they're just children, how could you checkmate children?
-   wwwwwwwwwwwwwwwwwwww - 20 W's in visible username, WGM title, and a patron to test ui for extremely wide usernames.

## Normal users:

The normal users have all the data. This includes notifications, ratings, follows, game histories, activity, timelines, blogs, forums, teams, tournaments. See the full list in spamdb/data/uids.txt
