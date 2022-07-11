#!/usr/bin/env python3
import pymongo
import argparse
import modules.forum as forum
import modules.event as event
import modules.user as user
import modules.blog as blog
import modules.game as game
import modules.team as team
import modules.util as util
import modules.tour as tour
from modules.datasrc import gen


def main():
    args = _get_args()

    gen.user_bg_mode = args.user_bg
    gen.default_password = args.password
    if args.users > -1:
        gen.set_num_uids(args.users)
    if args.teams > -1:
        gen.set_num_teams(args.teams)
    if args.dump_json:
        gen.set_json_dump_mode(args.dump_json)
    elif args.dump_bson:
        gen.set_bson_dump_mode(args.dump_bson)

    with _MongoContextMgr(args.uri) as db:
        user.create_user_colls(db, args)  # args.follow)
        game.create_game_colls(db, args)  # int(args.games))
        tour.create_tour_colls(db, args)  # int(args.tours))
        forum.create_forum_colls(db, args)  # int(int(args.posts) / 2))
        team.create_team_colls(db, args)  # int(int(args.posts) / 2))
        blog.create_blog_colls(db, args)  # int(args.blogs))
        event.create_event_colls(db, args)


class _MongoContextMgr:
    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)
        self.client.admin.command(
            "ping"
        )  # should raise an exception if we cant connect
        self.db = self.client.get_default_database()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed lila database with all kinds of spam."
    )
    parser.add_argument(
        "--uri",
        "-u",
        help=(
            'form: --uri="mongodb://user:password@host:port/database?'
            'authSource=default_db&authMechanism=SCRAM-SHA-256"  (default: '
            "mongodb://127.0.0.1/lichess)"
        ),
        default="mongodb://127.0.0.1/lichess",
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        help=(
            "generate users with this password rather than the default of "
            '"password".  recommended for exposed dev instances.  user '
            "creation will take longer due to bcrypt"
        ),
        default="password",
    )
    parser.add_argument(
        "--user-bg",
        "-b",
        type=int,
        help=(
            "force generated users to have this background set in their "
            "associated Pref object, 100 = light mode, 200 = dark mode, "
            "400 = transparent with random image.  (default: 200)"
        ),
        default=200,
    )
    parser.add_argument(
        "--users",
        type=int,
        default=-1,
        help=(
            "for large numbers of users, spamdb will postfix increasing numbers "
            "to the uids listed in data/uids.txt.  special users are not "
            "affected by this flag.  (default: # of lines in uids.txt)"
        ),
    )
    parser.add_argument(
        "--posts",
        type=int,
        help=(
            "total number of forum POSTS generated. teams get half, the 4 "
            "main categories get the other half.  (default: 4000)"
        ),
        default=4000,
    )
    parser.add_argument(
        "--blogs",
        type=int,
        help="(default: 20)",
        default=20,
    )
    parser.add_argument(
        "--teams",
        type=int,
        default=-1,
        help="(default: # of items in teams.txt)",
    )
    parser.add_argument(
        "--tours",
        type=int,
        default=80,
        help="(default: 80)",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=-1,
        help="(default/max = # of objects in game5.bson (around 3000))",
    )
    parser.add_argument(
        "--follow",
        type=float,
        default=0.16,
        help=(
            "follow factor is the fraction of all users that each user "
            "follows.  As it grows, so grow the collections."
            "(default: .16)"
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dump-bson",
        type=str,
        help="leave db alone, generate and dump BSONs to provided directory",
    )
    group.add_argument(
        "--dump-json",
        type=str,
        help="leave db alone, generate and dump JSONs to provided directory",
    )
    group.add_argument(
        "--no-create",
        action="store_true",
        help="skip object generation (usually in conjunction with --drop)",
    )
    parser.add_argument(
        "--drop",
        help=(
            "drop pre-existing collections prior to any update. see module code "
            "for specific collections dropped by each choice"
        ),
        choices=[
            "all",
            "game",
            "event",
            "forum",
            "team",
            "user",
            "blog",
            "tour",
        ],
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
