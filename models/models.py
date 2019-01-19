# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import *


engine = create_engine('''sqlite:///database.db''', connect_args={'check_same_thread': False}, poolclass=StaticPool)

metadata = MetaData(engine, reflect=True)

con = engine.connect()

try:
    user = metadata.tables['user']
    note = metadata.tables['note']
    access = metadata.tables['access']
except Exception as e:
    print("Nie udało się załadować tabeli")
con.close()


class UserModel():
    def get_user(self):
        con = engine.connect()
        user_full = con.execute(select([user]).fechall())
        con.close()
        return user_full

    def find_max_id(self):
        try:
            con = engine.connect()
            data = con.execute(select([func.max(user.c.id).label('user')])).scalar()
            con.close()
            if data != None:
                return data
            else:
                return 0
        except Exception as e:
            return 0

    def register_user(self, id, username, hashed_password):
        try:
            con = engine.connect()
            insert = user.insert().values(id=id, username=username, password=hashed_password)
            con.execute(insert)
            con.close()
        except Exception as e:
            con.close()


class NoteModel():
    def get_note(self):
        con = engine.connect()
        note_full = con.execute(select([note]).fechall())
        con.close()
        return note_full

    def add_note(self, id, note, owner, is_public):
        try:
            con = engine.connect()
            insert = user.insert().values(id=id, note=note, owner=owner, is_public=is_public)
            con.execute(insert)
            con.close()
        except Exception as e:
            con.close()
