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
            if not lookup:
                new_engine = database.DatabaseTypes(name=engine)
                self.db.session.add(new_engine)
                self.db.session.commit()

    def _target_exists_in_db(self, target):
        lookup = database.Targets.query.filter_by(url=target).first()
        if not lookup:
            return False
        else:
            return True

    def _lookup_type_id(self, id):
        if not id:
            return None
        lookup = database.DatabaseTypes.query.filter_by(id=id).first()
        if lookup:
            return lookup.name
        else:
            return None

    def read(self):
        lookup = database.Targets.query.all()
        for item in lookup:
            print("%s - %s - %s" % (item.id, item.url, self._lookup_type_id(item.db_typeid)))

    def add_target(self, target):
        if not self._target_exists_in_db(target):
            new_target = database.Targets(url=target)
            self.db.session.add(new_target)
            self.db.session.commit()

