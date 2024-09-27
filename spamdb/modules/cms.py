from modules.env import env
import modules.util as util

default_pages = [
    ['About', 'about'],
    ['Terms of Service', 'tos'],
    ['Privacy', 'privacy'],
    ['Title Verification', 'title-verify-index', '/verify-title'],
    ['Source Code', 'source'],
    ['Contribute', 'help'],
    ['Changelog', 'changelog'],
    ['Thank you!', 'thanks'],
    ['Ads', 'ads'],
    ['Chess Calendar', 'broadcast-calendar', '/broadcast/calendar'],
    ['About broadcasts', 'broadcasts', '/broadcast/help'],
    ['Lichess Broadcaster App', 'broadcaster-app', '/broadcast/app'],
    ['Puzzle Racer', 'racer'],
    ['Puzzle Storm', 'storm'],
    ['Studies: Staff Picks', 'studies-staff-picks'],
    ['Crazyhouse', 'variant-crazyhouse', '/variant/crazyhouse'],
    ['Chess960', 'variant-chess960', '/variant/chess960'],
    ['KingOfTheHill', 'variant-kingOfTheHill', '/variant/kingOfTheHill'],
    ['ThreeCheck', 'variant-threeCheck', '/variant/threeCheck'],
    ['Antichess', 'variant-antichess', '/variant/antichess'],
    ['Atomic', 'variant-atomic', '/variant/atomic'],
    ['Horde', 'variant-horde', '/variant/horde'],
    ['RacingKings', 'variant-racingKings', '/variant/racingKings'],
]


def update_cms_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.cms_page.drop()

    pages: list[CmsPage] = []

    for page in default_pages:
        pages.append(CmsPage(page))

    pages.append(CmsPage(['Mobile', 'mobile-apk'], empty=True))

    if args.no_create:
        return

    util.bulk_write(db.cms_page, pages)


class CmsPage:
    def __init__(self, page: list, empty=False):
        if empty:
            body = ''
        else:
            body = "\n\n".join([
                f'## {env.random_topic()}',
                f'{env.random_paragraph()}',
                f'### {env.random_topic()}',
                f'{env.random_paragraph()}',
                f'#### {env.random_topic()}',
                f'{env.random_paragraph()}',
            ])

        self._id = env.next_id(CmsPage)
        self.key = page[1]
        self.title = page[0]
        self.markdown = body
        self.language = 'en'
        self.live = True
        self.by = 'admin'
        self.at = util.time_since_days_ago(30)

        if len(page) > 2:
            self.canonicalPath = page[2]
