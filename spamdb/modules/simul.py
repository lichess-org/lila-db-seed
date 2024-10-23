import random
from string import ascii_letters, digits
from modules.env import env
import modules.util as util

def update_simul_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.simul.drop()

    simuls: list[Simul] = []

    for uid in env.uids:
        simuls.append(Simul(uid))

    if args.no_create:
        return

    util.bulk_write(db.simul, simuls)

class Simul:
    def __init__(self, uid: str) -> None:
        self._id = ''.join(random.sample(ascii_letters + digits, 8))
        self.name = uid
        self.status = 10
        self.clock = {
            'config': {
                'limitSeconds': random.randint(300, 1800),
                'incrementSeconds': random.randint(30, 180)
            },
            'hostExtraTime': random.randint(0, 60),
            'hostExtraTimePerPlayer': random.randint(0, 3)
        }
        self.applicants = []
        self.pairings = []
        self.variants = [1]
        self.createdAt = util.time_since_days_ago(1)
        self.hostId = uid.lower()
        self.hostRating = random.randint(1000, 2500)
        self.text = random.choice(env.topics)
        self.conditions = {}
        self.hostProvisional = random.choice([True, False])
        self.hostSeenAt = util.time_since_days_ago(1)
        self.color = random.choice(['white', 'black'])
        self.featurable = random.choice([True, False])
