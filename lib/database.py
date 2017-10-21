#!/usr/bin/env python3

## lib/database.py

import os
from sqlalchemy import Column, Text, Integer, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine(
    'sqlite:///%s' % os.path.join(basedir, 'data.sqlite'),
    connect_args={'check_same_thread': False}
)

Base = declarative_base()

class Targets(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    
Base.metadata.create_all(engine)

Scoped = scoped_session(
    sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=engine
    )
)

session = Scoped()
