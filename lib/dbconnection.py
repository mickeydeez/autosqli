#!/usr/bin/env python3

## lib/dbconnection.py

from lib import db, database

class DatabaseSession(object):

    def __init__(self):
        self.db = db
        self.db.create_all()
        self._init_db()

    def _init_db(self):
        for engine in ['mysql', 'postgres']:
            lookup = database.DatabaseTypes.query.filter_by(name=engine).first()
            if not lookup or len(lookup) == 0:
                new_engine = database.DatabaseTypes(name=engine)
                self.db.session.add(new_engine)
                self.db.session.commit()
