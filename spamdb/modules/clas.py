import random
from string import ascii_letters, digits
from faker import Faker
from modules.env import env
import modules.util as util
from modules.user import User

def update_clas_colls() -> None:
    args = env.args
    db = env.db
    fake = Faker()

    if args.drop:
        db.clas_clas.drop()
        db.clas_student.drop()
        db.clas_invite.drop()

    classes: list[Clas] = []
    students: list[Student] = []
    users: list[User] = []
    student_index = 0
    
    if args.classes < 1:
        return

    for clas_index in range(args.classes):
        clas_name = "Class " + str(clas_index + 1)
        clas_id = ''.join(random.sample(ascii_letters + digits, 8))
        classes.append({
            "_id": clas_id,
            "name": clas_name,
            "teachers": ["teacher"],
            "created": {
                "by": "teacher",
                "at": util.time_since_days_ago(2)
            },
            "desc": "Description for " + clas_name,
            "wall": "Last news",
            "viewedAt": util.time_since_days_ago(1)
        })

        if args.students < 1:
            continue
        for _ in range(args.students):
            student_index += 1
            students.append({
                "_id": "student" + str(student_index) + ":" + clas_id,
                "userId": "student" + str(student_index),
                "clasId": clas_id,
                "realName": fake.name(),
                "notes": "",
                "managed": True,
                "created": {
                    "by": "teacher",
                    "at": util.time_since_days_ago(1)
                }
            })
            users.append(User("student" + str(student_index), [], [], False))
            users[-1].kid = True

    if not args.no_create:
        util.bulk_write(db.clas_clas, classes)
        util.bulk_write(db.clas_student, students)
        util.bulk_write(db.user4, users)
    return classes


class Clas:
    def __init__(self, clas: dict):
        self._id = clas["_id"]
        self.name = clas["name"]
        self.desc = clas["desc"]
        self.wall = clas["wall"]
        self.teachers = clas["teachers"]
        self.created = clas["created"]
        self.viewedAt = clas["viewedAt"]


class Student:
    def __init__(self, student: dict):
        self._id = student["_id"]
        self.userId = student["userId"]
        self.clasId = student["clasId"]
        self.realName = student["realName"]
        self.notes = student["notes"]
        self.managed = student["managed"]
        self.created = student["created"]


class Invite:
    def __init__(self, invite: dict):
        self._id = invite["_id"]
        self.userId = invite["userId"]
        self.realName = invite["realName"]
        self.clasId = invite["clasId"]
        self.created = invite["created"]
