#!/usr/bin/env python3
import pymongo
import modules.forum as forum
import modules.event as event
import modules.user as user
import modules.blog as blog
import modules.cms as cms
import modules.feed as feed
import modules.game as game
import modules.team as team
import modules.tour as tour
import modules.msg as msg
import modules.search as search
import modules.video as video
import modules.study as study
from modules.env import env

def main():
    with _MongoContextMgr(env.args.uri, env.args.drop_db) as db:
        env.db = db
        user.update_user_colls()
        games = game.update_game_colls()
        tour.update_tour_colls()
        posts = forum.update_forum_colls()
        teams = team.update_team_colls()
        msg.update_msg_colls()
        blog.update_blog_colls()
        feed.update_feed_colls()
        cms.update_cms_colls()
        event.update_event_colls()
        video.update_video_colls()
        studies = study.update_study_colls()
        if env.args.es:
            search.update_elasticsearch(env.args.es_host, games, posts, teams, studies)

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

if __name__ == "__main__":
    main()
