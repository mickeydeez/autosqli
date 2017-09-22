#!/usr/bin/python

import bs4
import requests
import re
from os import path
from sys import exit
from time import sleep
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from argparse import ArgumentParser


def run():
    args = parse_args()
    if args.db_path:
        if args.scan:
            dork = Dorker(db=args.db_path)
            dork.run_scan()
            dork.read()
        else:
            dork = Dorker(db=args.db_path)
            dork.read()
    elif args.scan:
        dork = Dorker()
        dork.run_scan()
        dork.read()

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-d',
        '--database',
        action='store',
        dest='db_path',
        help="Path to pre-generated sqlite database"
    )
    parser.add_argument(
        '-s',
        '--scan',
        action='store_const',
        const=True,
        dest='scan',
        help="Run a scan against the defined queries"
    )
    args = parser.parse_args()
    if not args.scan and not args.db_path:
        parser.print_help()
        exit(1)
    return args

class Dorker(object):

    def __init__(self, db=None):
        #self.queries = ["inurl%3A+.php%3Fid%3D1","inurl%3A+.php%3Fid%3D2","inurl%3A+.php%3Fid%3D3",
        #            "inurl%3A+.php%3Fid%3D4","inurl%3A+.php%3Fid%3D5","inurl%3A+.php%3Fid%3D6",
        #            "inurl%3A+.php%3Fid%3D7","inurl%3A+.php%3Fid%3D8","inurl%3A+.php%3Fid%3D9",
        #            "inurl%3A+search.php%3Fq%3D",]
        self.queries = ["inurl%3A+.php%3Fid%3D1","inurl%3A+.php%3Fid%3D2","inurl%3A+.php%3Fid%3D3"]
        self.engine = Flask(__name__)
        self.engine.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
        self.engine.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if db:
            self._load_db(db)
        else:
            self._init_db()

    def _init_db(self):
        basedir = path.abspath(path.dirname(__file__))
        self.engine.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(basedir, 'data.sqlite')
        self.db = SQLAlchemy(self.engine)
        self._define_tables()
    
    def _load_db(self, db):
        self.engine.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db
        self.db = SQLAlchemy(self.engine)
        self._define_tables()

    def _define_tables(self):
        class VulnerableSites(self.db.Model):
            __tablename__ = 'vulnerable_sites'
            id = self.db.Column(self.db.Integer, primary_key=True)
            url = self.db.Column(self.db.Text)
        self.db.create_all()
        self.table = VulnerableSites

    def read(self):
        results = self.table.query.all()
        for item in results:
            print(item.url)

    def run_scan(self):
        results = self.get_endpoints()
        self.test_endpoints(results)

    def get_endpoints(self):
        results = []
        for query in self.queries:
            print("Trying %s" % query)
            address= "https://www.google.co.uk/search?q=%s" % query
            page = requests.get(address)
            if re.search('captcha', page.text):
                print("Detected captcha")
            else:
                with open("%s.txt" % query, 'w') as f:
                    f.write(page.text)
                soup = bs4.BeautifulSoup(page.text,"html.parser")
                for item in soup.find_all('h3', attrs={'class' : 'r'}):
                    results.append(item.a['href'][7:])
                print("Finished %s. Sleeping for 5 seconds" % query)
            sleep(5)
        return results

    def test_endpoints(self, results):
        relist = ["sql", "syntax"]
        for item in results:
            print("Testing %s" % item)
            try:
                response = requests.get("%s'" % item)
            except:
                print("Yucky URL: %s'" % item)
                pass
            for regex in relist:
                if re.search(regex, response.text.lower()):
                    site = self.table(url=item)
                    self.db.session.add(site)
                    self.db.session.commit()
                    break
                else:
                    continue


if __name__ == '__main__':
    run()
