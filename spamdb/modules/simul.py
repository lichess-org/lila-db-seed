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
                'limitSeconds': random.choice([10, 20, 60, 90]) * 60,
                'incrementSeconds': random.choice([0, 5, 10, 15, 20]),
            },
            'hostExtraTime': random.choice([0, 5, 10, 15, 20]),
            'hostExtraTimePerPlayer': random.choice([0, 10, 20, 30, 40]),
        }
        self.applicants = []
        self.pairings = []
        self.variants = [1]
        self.createdAt = util.time_since_days_ago(1)
        self.hostId = uid.lower()
        self.hostRating = random.randint(1000, 2500)
        self.text = random.choice(env.topics)
        self.conditions = {}
        self.hostProvisional = False
        self.hostSeenAt = util.time_since_days_ago(1)
        self.color = random.choice(['white', 'black'])
        self.featurable = random.choice([True, False])
