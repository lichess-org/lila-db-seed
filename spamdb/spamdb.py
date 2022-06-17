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
    if args.users > -1:
        gen.set_num_uids(args.users)
    if args.teams > -1:
        gen.set_num_teams(args.teams)
    gen.user_bg_mode = args.user_bg
    with _MongoContextMgr(args.uri) as db:

        _do_drops(db, args.drop)

        if args.dump_json:
            gen.set_json_dump_mode(args.dump_json)
        elif args.dump_bson:
            gen.set_bson_dump_mode(args.dump_bson)

        if not args.no_create:
            user.create_user_colls(db, args.follow)
            game.create_game_colls(db, int(args.games))
            tour.create_tour_colls(db, int(args.tours))
            forum.create_forum_colls(db, int(int(args.posts) / 2))
            team.create_team_colls(db, int(int(args.posts) / 2))
            blog.create_blog_colls(db, int(args.blogs))
            event.create_event_colls(db)

        if args.insert:
            util.insert_json(db, args.insert)


def _do_drops(db: pymongo.MongoClient, drop) -> None:
    if drop == "game":
        game.drop(db)
    elif drop == "event":
        event.drop(db)
    elif drop == "forum":
        forum.drop(db)
    elif drop == "team":
        team.drop(db)
    elif drop == "user":
        user.drop(db)
    elif drop == "blog":
        blog.drop(db)
    elif drop == "tour":
        tour.drop(db)
    elif drop == "all":
        tour.drop(db)
        game.drop(db)
        event.drop(db)
        forum.drop(db)
        team.drop(db)
        user.drop(db)
        blog.drop(db)


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
        help=(
            'form: --uri="mongodb://user:password@host:port/database?'
            'authSource=default_db&authMechanism=SCRAM-SHA-256"  (default: '
            "mongodb://127.0.0.1/lichess)"
        ),
        default="mongodb://127.0.0.1/lichess",
    )
    parser.add_argument(
        "-u",
        "--users",
        type=int,
        default=-1,
        help="(defaults to number of names in uids.txt)",
    )
    parser.add_argument(
        "-bg",
        "--user-bg",
        type=int,
        help=(
            "force generated users to have this background set in their "
            "associated Pref object, 100 = light mode, 200 = dark mode, "
            "400 = transparent with random image.  (default: 200)"
        ),
        default=200,
    )
    parser.add_argument(
        "-p",
        "--posts",
        type=int,
        help=(
            "total number of forum POSTS generated. teams get half, the 4 "
            "main categories get the other half.  (default: 4000)"
        ),
        default=4000,
    )
    parser.add_argument(
        "-b",
        "--blogs",
        type=int,
        help="(default: 20)",
        default=20,
    )
    parser.add_argument(
        "-te",
        "--teams",
        type=int,
        default=-1,
        help="(default: # of items in teams.txt)",
    )
    parser.add_argument(
        "-to",
        "--tours",
        type=int,
        default=80,
        help="(default: 80)",
    )
    parser.add_argument(
        "-g",
        "--games",
        type=int,
        default=-1,
        help="(default/max = # of objects in game5.bson (prolly 3000))",
    )
    parser.add_argument(
        "-f",
        "--follow",
        type=float,
        default=0.16,
        help=(
            "follow factor is the fraction of all users that each user "
            "follows (for timeline/activity/friend/notification work).  "
            "(default: .16)"
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--dump-bson",
        type=str,
        help="leave db alone, generate and dump BSONs to provided directory",
    )
    group.add_argument(
        "-dj",
        "--dump-json",
        type=str,
        help="leave db alone, generate and dump JSONs to provided directory",
    )
    group.add_argument(
        "-nc",
        "--no-create",
        action="store_true",
        help=(
            "skip procedural object generation (usually in conjunction with "
            "--drop or --insert)"
        ),
    )
    parser.add_argument(
        "-i",
        "--insert",
        type=str,
        help=(
            "insert contents of file specified by INSERT parameter as json into "
            "one or more collections. -nc/--no-create does NOT suppress insertion "
            "so use that to limit db updates to this insert.  contents must have "
            "the form {collname:[listOfObjs]} see example at "
            "data/create-blog-categ.json"
        ),
    )

    parser.add_argument(
        "--drop",
        help=(
            "useful during development of this utility but beware!  multiple "
            "collections dropped by each choice:  see code"
        ),
        choices=[
            "game",
            "event",
            "forum",
            "team",
            "user",
            "blog",
            "all",
            "tour",
        ],
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
