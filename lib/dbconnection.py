#!/usr/bin/env python3

## lib/dbconnection.py

from lib.database import Base, Targets, session, engine

class DatabaseSession(object):

    def __init__(self):
        self.base = Base
        self.session = session
        self.engine = engine
        self.base.metadata.create_all(self.engine)

    def _target_exists_in_db(self, target):
        lookup = self.session.query(Targets).filter_by(url=target).first()
        if not lookup:
            return False
        else:
            return True

    def read(self):
        lookup = self.session.query(Targets).all()
        for item in lookup:
            print("%s - %s" % (item.id, item.url))

    def add_target(self, target):
        if not self._target_exists_in_db(target):
            new_target = Targets(url=target)
            self.session.add(new_target)
            self.session.commit()

