import random
from modules.datasrc import gen


class Pref:
    def __init__(self, uid: str):
        self._id = uid
        self.is3d = False
        self.bg = 400  # random.choice([100, 200, 400]) # you did the work, now make em look at it!
        if self.bg == 400:
            self.bgImg = gen.randomImageLink()

        # can't imagine there's anything here that would be useful for testing since it's quick to
        # modify prefs directly
