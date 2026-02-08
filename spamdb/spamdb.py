#!/usr/bin/env python3

def main():
    import pymongo
    import modules.forum as forum
    import modules.event as event
    import modules.user as user
    import modules.blog as blog
    import modules.cms as cms
    import modules.feed as feed
    import modules.puzzle as puzzle
    import modules.storm as storm
    import modules.simul as simul
    import modules.analysis as analysis
    import modules.game as game
    import modules.team as team
    import modules.tour as tour
    import modules.msg as msg
    import modules.video as video
    import modules.study as study
    import modules.jsbot as jsbot
    import modules.clas as clas
    from modules.env import env

    if env.args.list_ratings:
        for u in env.uids:
            print(f'{u} {env.stable_rating(u)}')
        return

    class _MongoContextMgr:
        def __init__(self, uri: str, drop_db: bool = False):
            self.client = pymongo.MongoClient(uri)
            self.client.admin.command('ping')  # should raise an exception if we cant connect
            self.db = self.client.get_default_database()
            if drop_db:
                self.client.drop_database(self.db)

        def __enter__(self):
            return self.db

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.client.close()

    with _MongoContextMgr(env.args.uri, env.args.drop_db) as db:
        env.db = db
        user.update_user_colls()
        game.update_game_colls()
        tour.update_tour_colls()
        forum.update_forum_colls()
        team.update_team_colls()
        msg.update_msg_colls()
        blog.update_blog_colls()
        feed.update_feed_colls()
        puzzle.update_puzzle_colls()
        storm.update_storm_colls()
        simul.update_simul_colls()
        analysis.update_analysis_colls()
        cms.update_cms_colls()
        event.update_event_colls()
        video.update_video_colls()
        study.update_study_colls()
        jsbot.update_jsbot_colls()
        clas.update_clas_colls()


if __name__ == '__main__':
    main()
