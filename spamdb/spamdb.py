#!/usr/bin/env python3
import pymongo
import argparse
import modules.forum as forum
import modules.event as event
import modules.user as user
import modules.blog as blog
import modules.game as game
import modules.team as team
import modules.tour as tour
import modules.msg as msg
import modules.search as search
from modules.seed import env


def main():
    env.set_args(_get_args())

    with _MongoContextMgr(env.args.uri, env.args.drop_db) as db:
        env.db = db
        user.update_user_colls()
        games = game.update_game_colls()
        tour.update_tour_colls()
        posts = forum.update_forum_colls()
        teams = team.update_team_colls()
        msg.update_msg_colls()
        blog.update_blog_colls()
        event.update_event_colls()
        if env.args.es:
            search.update_elasticsearch(env.args.es_host, games, posts, teams)


class _MongoContextMgr:
    def __init__(self, uri, drop_db=False):
        self.client = pymongo.MongoClient(uri)
        self.client.admin.command("ping")  # should raise an exception if we cant connect
        self.db = self.client.get_default_database()
        if drop_db:
            self.client.drop_database(self.db)

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""
            seed lila database with the finest spam.
        """
    )
    parser.add_argument(
        "--uri",
        "-u",
        help="""
            form: --uri="mongodb://user:password@host:port/database?
            authSource=default_db&authMechanism=SCRAM-SHA-256"  (default:
            mongodb://127.0.0.1/lichess)
        """,
        default="mongodb://127.0.0.1/lichess",
    )
    parser.add_argument(
        "--es",
        action="store_true",
        help="""
            create elasticsearch indices for games, posts, and teams to allow
            search functionality in lila.
        """,
    )
    parser.add_argument(
        "--es-host",
        help="""
            elasticsearch host and port (default: localhost:9200)
        """,
        default="localhost:9200",
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        help="""
            supply your own default password. this is highly recommended for
            exposed dev instances. note: different values may be assigned to
            specific users in data/uids.txt. uids.txt passwords will override this
            argument for the specified user only. (default: password)
        """,
        default="password",
    )
    parser.add_argument(
        "--su-password",
        type=str,
        help="""
            supply a password for admin and moderator users. this is needed for
            exposed dev instances. this argument will override any other defaults
            or values given in data/uids.txt.
        """,
    )
    parser.add_argument(
        "--user-bg",
        "-b",
        type=int,
        help="""
            generated users will have this background set in their associated
            Pref object, 100 = light mode, 200 = dark mode, 400 = transparent
            with random image from data/image_links.txt. (default: 200)
        """,
        default=200,
        choices=[100, 200, 400],
    )
    parser.add_argument(
        "--users",
        type=int,
        help="""
            how many normal users to generate. for large values, spamdb will
            postfix increasing numbers to the uids listed in data/uids.txt.
            special users are always generated and are not affected by this flag.
            users with postfixed numbers get the default password. (default:
            # of users in data/uids.txt)
        """,
    )
    parser.add_argument(
        "--forum-posts",
        type=int,
        help="""
            approximate number of POSTS generated for teams and regular forums
            (default: 200)
        """,
        default=200,
    )
    parser.add_argument(
        "--ublog-posts",
        type=int,
        help="(default: 20)",
        default=20,
    )
    parser.add_argument(
        "--teams",
        type=int,
        help="(default: # of teams in data/teams.txt)",
    )
    parser.add_argument(
        "--membership",
        type=float,
        default=0.25,
        help="""
            team membership ratio to total users from 0 (empty aside from leaders)
            to 1 (each team contains all users) (default: .25)
        """,
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
        help="(default/max = # of objects in data/game5.bson (around 3000))",
    )
    parser.add_argument(
        "--follow",
        type=float,
        default=0.16,
        help="""
            follow factor is the fraction of all users that each user
            follows.  for work on timelines, notifications, friend features,
            you can set this to 1 for a fully connected graph of normal users.
            (default: .16)
        """,
    )
    parser.add_argument(
        "--no-timeline",
        "-n",
        action="store_true",
        help="""
            timeline entries are constructed with unique object ids from pymongo's
            bson module. their ids will not match on subsequent spamdb upserts
            and therefore they keep accumulating unless you --drop or --drop-db.
            if you do not wish to drop anything, you may also prevent entries
            from accumulating by including the --no-timeline argument. this will
            suppress their generation for this run.
        """,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dump-bson",
        type=str,
        help="leave db alone. generate and dump BSONs to provided directory",
    )
    group.add_argument(
        "--dump-json",
        type=str,
        help="leave db alone. generate and dump JSONs to provided directory",
    )
    group.add_argument(
        "--no-create",
        action="store_true",
        help="""
            skip database in/upserts. useful for testing the object generation
            code or just erasing spamdb stuff in conjunction with --drop
        """,
    )
    drops = parser.add_mutually_exclusive_group()
    drops.add_argument(
        "--drop",
        action="store_true",
        help="""
            drop spamdb managed collections prior to any object creation. others
            will be left alone.
        """,
    )
    drops.add_argument(
        "--drop-db",
        action="store_true",
        help="""
        drop lichess database prior to any object creation.
        """,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
