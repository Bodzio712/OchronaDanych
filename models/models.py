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

    def update_password(self, username, hashed_password):
        try:
            con = engine.connect()
            update = user.update().where(user.c.username == username).values(password=hashed_password)
            con.execute(update)
            con.close()
        except:
            con.close()


class NoteModel():
    def get_note(self, username):
        con = engine.connect()
        try:
            note_full = con.execute("SELECT * FROM note").fetchall()
        except Exception as e:
            x=1
        con.close()
        return note_full

    def get_all_note(self):
        con = engine.connect()
        try:
            note_full = con.execute("SELECT * FROM note WHERE is_public = 'true'").fetchall()
        except Exception as e:
            x=1
        con.close()
        return note_full

    def get_priavte_note(self, username):
        con = engine.connect()
        try:
            note_full = con.execute("SELECT * FROM note WHERE is_public = 'false' AND owner = '" + username +"'").fetchall()
        except Exception as e:
            note_full = null
        con.close()
        return note_full

    def get_shared(self, username):
        con = engine.connect()
        try:
            note_full = con.execute("SELECT note.id, note.owner, note.note, note.is_public "
                                    + "FROM note "
                                    + "INNER JOIN access ON access.note_id = note.id "
                                    + "WHERE access.username = '" + username + "' AND note.is_public != 'true'").fetchall()
        except Exception as e:
            note_full = null
        con.close()
        return note_full



    def find_max_id(self):
        try:
            con = engine.connect()
            data = con.execute(select([func.max(note.c.id).label('note')])).scalar()
            con.close()
            if data != None:
                return data
            else:
                return 0
        except Exception as e:
            return 0

    def add_note(self, id, notes, owner, is_public):
        try:
            con = engine.connect()
            insert = note.insert().values(id=id, note=notes, owner=owner, is_public=is_public)
            con.execute(insert)
            con.close()
        except Exception as e:
            con.close()


class AccessModel():
    def get_access(self):
        con = engine.connect()
        try:
            access_full = con.execute("SELECT * FROM access").fetchall()
        except Exception as e:
            con.close()
        return access_full

    def find_max_id(self):
        try:
            con = engine.connect()
            data = con.execute(select([func.max(access.c.id).label('access')])).scalar()
            con.close()
            if data != None:
                return data
            else:
                return 0
        except Exception as e:
            return 0

    def add_access(self, id, username, note_id):
        try:
            con = engine.connect()
            insert = access.insert().values(id=id, username=username, note_id=note_id)
            con.execute(insert)
            con.close()
        except Exception as e:
            con.close()
