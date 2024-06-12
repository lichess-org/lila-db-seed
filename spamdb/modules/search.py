import json
import http.client
from modules.env import env
from modules.game import Game
from modules.forum import Post
from modules.team import Team
from modules.perf import clock_to_perf
from modules.study import Study

def update_elasticsearch(hostport: str, games: list[Game], posts: list[Post], teams: list[Team], studies: list[Study]) -> None:
    host, port = hostport.split(":")
    es = http.client.HTTPConnection(host, port)
    try:
        ngames = _make_indices(es, "game", _game_mapping, games, _game_to_index)
        nposts = _make_indices(es, "forum", _forum_mapping, posts, _post_to_index)
        nteams = _make_indices(es, "team", _team_mapping, teams, _team_to_index)
        nstudy = _make_indices(es, "study", _study_mapping, studies, study_to_index)
        es.close()

        print(f"elasticsearch........... {{game: {ngames}, forum: {nposts}, team: {nteams}, study: {nstudy}}}")
    except Exception as e:
        if es.sock:
            print(f"elasticsearch........... failed: {e}")
        else:
            print("elasticsearch........... skipped, not running")

def _make_indices(
    es: http.client.HTTPConnection, index: str, mapping: dict, objects: list, builder
) -> int:
    es.request("DELETE", f"/{index}")
    es.getresponse().read()
    es.request(
        "PUT",
        f"/{index}",
        json.dumps(mapping),
        {"content-type": "application/json; charset=UTF-8"},
    )
    rsp = es.getresponse()
    if rsp.status // 100 != 2:
        print(f"elasticsearch: PUT /{index} failed:")
        print(rsp.read(77) + "...")
        return 0
    rsp.read()

    bulk_ndjson = ""
    for it in objects:
        bulk_ndjson += builder(it)

    es.request(
        "POST",
        f"/{index}/_bulk",
        bulk_ndjson,
        {"content-type": "application/x-ndjson; charset=UTF-8"},
    )
    rsp = es.getresponse()
    if rsp.status // 100 != 2:
        print(f"elasticsearch: POST /{index}/_bulk failed:")
        print(rsp.read(77) + "...")
        return 0
    rsp.read()

    return len(objects)


def _game_to_index(g: Game) -> str:
    r1 = env.fide_map[g.us[0]]
    r2 = env.fide_map[g.us[1]]
    gi = {
        "s": g.s,
        "u": g.us,
        "d": g.ua.strftime("%Y-%m-%d %H:%M:%S"),
        "so": g.so,
        "a": round(((1500 if r1 == None else r1) + (1500 if r2 == None else r2)) / 2),
        "wu": g.us[0],
        "bu": g.us[1],
        "t": round(g.t / 2),
        "n": g.an,
        "ct": g.c[0] * 60,
        "ci": g.c[1],
        "l": round(g.c[0] * 115),
        "r": g.ra,
        "p": clock_to_perf(g.c[0], g.c[1]),
    }
    if "wid" in g.__dict__:
        gi["w"] = g.wid
        gi["o"] = g.us[0] if g.wid == g.us[1] else g.us[1]
        gi["c"] = 1 if g.wid == g.us[0] else 2

    op = {"index": {"_index": "game", "_id": g._id, "_type": "_doc"}}
    return json.dumps(op, indent=None) + "\n" + json.dumps(gi, indent=None) + "\n"


def _post_to_index(p: Post):
    pi = {
        "bo": p.text,
        "to": p.topic,
        "ti": p.topicId,
        "au": p.userId,
        "tr": p.troll,
        "da": p.createdAt.timestamp() * 1000,
    }
    op = {"index": {"_index": "forum", "_id": p._id, "_type": "_doc"}}
    return json.dumps(op, indent=None) + "\n" + json.dumps(pi, indent=None) + "\n"


def _team_to_index(t: Team) -> str:
    ti = {"na": t.name, "de": t.description, "nbm": t.nbMembers}
    op = {"index": {"_index": "team", "_id": t._id, "_type": "_doc"}}
    return json.dumps(op, indent=None) + "\n" + json.dumps(ti, indent=None) + "\n"

def study_to_index(s: Study) -> str:
    si = {
        "name": s.name,
        "owner": s.ownerId,
        "members": list(s.members.keys()),
        "chapterNames": " ",
        "chapterTexts": " ",
        "topics": s.topics if s.topics else " ",
        "likes": s.likes,
        "public": s.visibility == "public",
    }
    op = {"index": {"_index": "study", "_id": s._id, "_type": "_doc"}}
    return json.dumps(op, indent=None) + "\n" + json.dumps(si, indent=None) + "\n"

_game_mapping = {
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    },
    "mappings": {
        "properties": {
            "s": {"type": "keyword", "doc_values": False},
            "t": {"type": "short", "doc_values": True},
            "r": {"type": "boolean", "doc_values": False},
            "p": {"type": "keyword", "doc_values": False},
            "u": {"type": "keyword", "doc_values": False},
            "w": {"type": "keyword", "doc_values": False},
            "o": {"type": "keyword", "doc_values": False},
            "c": {"type": "keyword", "doc_values": False},
            "a": {"type": "short", "doc_values": True},
            "i": {"type": "short", "doc_values": False},
            "d": {"type": "date", "doc_values": True, "format": "yyyy-MM-dd HH:mm:ss"},
            "l": {"type": "integer", "doc_values": False},
            "ct": {"type": "integer", "doc_values": False},
            "ci": {"type": "short", "doc_values": False},
            "n": {"type": "boolean", "doc_values": False},
            "wu": {"type": "keyword", "doc_values": False},
            "bu": {"type": "keyword", "doc_values": False},
            "so": {"type": "keyword", "doc_values": False},
        },
    },
}

_team_mapping = {
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    },
    "mappings": {
        "properties": {
            "na": {"type": "text", "analyzer": "english", "boost": 10.0},
            "de": {"type": "text", "analyzer": "english", "boost": 2.0},
            "nbm": {"type": "short"},
        },
    },
}

_forum_mapping = {
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    },
    "mappings": {
        "properties": {
            "bo": {"type": "text", "analyzer": "english", "boost": 2.0},
            "to": {"type": "text", "analyzer": "english", "boost": 5.0},
            "au": {"type": "keyword", "doc_values": False},
            "ti": {"type": "keyword", "doc_values": False},
            "tr": {"type": "boolean", "doc_values": False},
            "da": {"type": "date"},
        },
    },
}

_study_mapping = {
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    },
    "mappings": {
        "properties": {
            "name": {"type": "text", "analyzer": "english", "boost": 10.0},
            "owner": {"type": "keyword", "doc_values": False, "boost": 2.0},
            "members": {"type": "keyword", "doc_values": False, "boost": 1.0},
            "chapterNames": {"type": "text", "analyzer": "english", "boost": 4.0},
            "chapterTexts": {"type": "text", "analyzer": "english", "boost": 1.0},
            "topics": {"type": "text", "analyzer": "english", "boost": 5.0},
            "likes": {"type": "short", "doc_values": True},
            "public": {"type": "boolean", "doc_values": False},
        },
    },
}
