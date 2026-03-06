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
    ['Your account has been closed', 'appeal-landing'],
    ['Your account has been closed by your teacher', 'account-closed-by-teacher'],
    ['Account deletion is pending', 'delete-done', '/account/delete/done'],
    ['Team Etiquette', 'team-etiquette'],
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
    pages.append(CmsPage(['Test Users', 'test-users'], body=_seeded_users_body()))

    if args.no_create:
        return

    util.bulk_write(db.cms_page, pages)


def _seeded_users_body() -> str:
    patron_users = [f'patron{i}' for i in list(range(1, 13)) + [24, 36, 48, 60]] + ['lifetime']
    bot_users = [f'bot{i}' for i in range(10)]

    def ul(items: list[str]) -> str:
        return '\n'.join(f'- {item}' for item in items)

    sections = [
        '## Special Users',
        (
            'Default password for all users: **password**\n\n'
        ),
        '### Admin & Moderator Roles',
        ul([
            '**superadmin** — ROLE_SUPER_ADMIN',
            '**admin** — ROLE_ADMIN',
            '**shusher** — ROLE_SHUSHER',
            '**hunter** — ROLE_CHEAT_HUNTER',
            '**puzzler** — ROLE_PUZZLE_CURATOR',
            '**editor** — ROLE_PAGES',
            '**events** — ROLE_MANAGE_EVENT',
            '**api** — ROLE_API_HOG',
        ]),
        '### Other Roles',
        ul([
            '**broadcaster**',
            '**coach** — ROLE_COACH',
            '**teacher** — ROLE_TEACHER',
        ]),
        '### Marked Users',
        ul([
            '**troll** — troll mark (shadow-banned)',
            '**rankban** — rankban mark',
            '**reportban** — reportban mark',
            '**alt** — alt mark',
            '**boost** — boost mark',
            '**engine** — engine mark',
        ]),
        '### Other Special Users',
        ul([
            '**playban** — has an active playban',
            '**zerogames** — no game history',
            '**kid** — kid mode enabled',
            '**wwwwwwwwwwwwwwwwwwww** — 20 W\'s, WGM title, patron',
        ]),
        '### Student Accounts',
        '(all in kid mode, managed by **teacher**)\n\n'
        + ', '.join(
            f'**student{i}**'
            for i in range(1, env.args.classes * env.args.students + 1)
        ),
        '### Bots',
        '(bot0-bot2 are verified)\n\n' + ', '.join(f'**{b}**' for b in bot_users),
        '### Patron Users',
        ', '.join(f'**{p}**' for p in patron_users),
        '## Normal Users',
        ', '.join(f'**{uid}**' for uid in env.uids),
    ]

    return '\n\n'.join(sections)


class CmsPage:
    def __init__(self, page: list, empty=False, body: str | None = None):
        if body is not None:
            content = body
        elif empty:
            content = ''
        else:
            content = '\n\n'.join(
                [
                    f'## {env.random_topic()}',
                    f'{env.random_paragraph()}',
                    f'### {env.random_topic()}',
                    f'{env.random_paragraph()}',
                    f'#### {env.random_topic()}',
                    f'{env.random_paragraph()}',
                ]
            )
        body = content

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
