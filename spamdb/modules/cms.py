from modules.env import env
import modules.util as util

default_pages = [
    ('about', 'About'),
    ('tos', 'Terms of Service'),
    ('privacy', 'Privacy'),
    ('master', 'Title Verification'),
    ('source', 'Source Code'),
    ('help', 'Contribute'),
    ('changelog', 'Changelog'),
    ('thanks', 'Thank you!'),
    ('ads', 'Ads'),
]


def update_cms_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.cms_page.drop()

    pages: list[CmsPage] = []

    for slug, title in default_pages:
        pages.append(CmsPage(slug, title))

    if args.no_create:
        return

    util.bulk_write(db.cms_page, pages)


class CmsPage:
    def __init__(self, slug: str, title: str):
        self._id = env.next_id(CmsPage)
        self.key = slug
        self.canonicalPath = f'/{slug}'
        self.title = title
        self.markdown = env.random_paragraph()
        self.language = 'en'
        self.live = True
        self.by = 'admin'
        self.at = util.time_since_days_ago(30)
