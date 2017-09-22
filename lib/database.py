#!/usr/bin/env python3

## lib/database.py

from lib import db

class DatabaseTypes(db.Model):
    __tablename__ = 'database_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    targets = db.relationship('Targets', backref='database_types')

class Targets(db.Model):
    __tablename__ = 'targets'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)
    db_typeid = db.Column(db.Integer, db.ForeignKey('database_types.id'))
    
class Queries(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key=True)
