# Database data for development on ornicar/lila

## Usage:

```
mongorestore dump
```

## Contents:

- 3000 puzzles (also see this [full puzzle DB](https://database.lichess.org/#puzzles) in CSV format)
- 2036 puzzle paths, required by lila to find the puzzles
- 3000 games from which the puzzles were made, required by lila to use the puzzles
- lots of other stuff including users & mods. see below

```

```

---

# Create your own database:

If you want to customize database size, users, text, forum categories, teams, images, blogs, etc. then use the provided spamdb.py utility (feel free to improve the code). spamdb.py will insert into mongodb directly and can export jsons and bsons. Most of the bsons in dump were generated with spamdb.py. Usage help:

```
python3 ./spamdb.py --help
```

python3.9+ and pymongo module are both required. get pymongo with:

```
pip3 install pymongo
```

## Special users:

- lichess/password - ROLE_SUPER_ADMIN # lichess mod such power!
- boost-hunter/password - ROLE_BOOST_HUNTER # mod ui is very robust
- shusher/password - ROLE_SHUSHER
- cheat-hunter/password - ROLE_CHEAT_HUNTER
- troll/password - marked as troll
- bot/password - marked as bot
- kid/password - they're just children, how could you checkmate children?
- wide/password - 20 W's in visible username, WGM title, and a patron. It's the widest possible (for ui testing)

## Normal users:

userids found in users.txt, chosen from international baby names. All accounts created by spamdb.py utilize "password" as their password. The normal users have all the data: the follows, the notifications, the ratings, the game histories, the timelines. You're missing out if you don't take svetlana or marcel for a spin

## Caveats:

Right now game search doesn't work at all.
