import random
from datetime import datetime
from modules.seed import env
import modules.util as util


def update_msg_colls() -> None:
    args = env.args
    db = env.db

    if args.drop:
        db.msg_msg.drop()
        db.msg_thread.drop()

    msgs: list[Msg] = []
    threads: dict[str, MsgThread] = {}  # thread id -> thread

    for u1 in env.uids:
        for u2 in random.sample(env.uids, int(0.25 * len(env.uids))):
            if u1 == u2 or threads.get(_tid(u1, u2)) != None:
                continue
            msgs.append(Msg(u1, u2, util.time_since_days_ago()))
            while util.chance(0.85):
                msgs.append(Msg(u1, u2, util.time_shortly_after(msgs[-1].date)))

            threads[_tid(u1, u2)] = MsgThread(u1, u2, msgs[-1])

    util.bulk_write(db.msg_msg, msgs)
    util.bulk_write(db.msg_thread, threads.values())


def _tid(u1: str, u2: str):
    return f"{u1}/{u2}" if u1 < u2 else f"{u2}/{u1}"


class Msg:
    def __init__(self, u1: str, u2: str, date: datetime):
        self._id = env.next_id(Msg)
        self.tid = _tid(u1, u2)
        self.text = random.choice(env.msgs)
        self.user = u1 if util.chance(0.5) else u2
        self.date = date


class MsgThread:
    def __init__(self, u1: str, u2: str, lastMsg: Msg):
        self._id = _tid(u1, u2)
        self.users = [u1, u2]
        self.__dict__["del"] = []
        self.lastMsg = {
            "text": lastMsg.text,
            "date": lastMsg.date,
            "user": lastMsg.user,
            "read": True,
        }
