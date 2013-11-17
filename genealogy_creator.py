# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 15:08:25 2013

@author: Aitor
"""

import re
import urllib2
import networkx as nx

BASE_URL = 'http://en.wikipedia.org'

# Advisors appear both as doctoral and academic advisors
SEC_DOCTORAL = 'Doctoral advisor'
SEC_ACADEMIC = 'Academic advisor'
SEC_STUDENTS = 'Notable students'
SEC_END = '</tr>'

WIKI_PERSON = '\/wiki/\D+\"'

G = nx.DiGraph()

# already processed persons
proccessed = []
    
def get_advisors(page):
    p = re.compile(WIKI_PERSON)
    lines = page.split('\n')
    
    advisor_start = False   

    advisors = []

    
    for line in lines:
        if advisor_start:
            if SEC_END in line:
                break
            matches = p.findall(line)
            for m in matches:
                advisor= m.split('"')[0]
                advisors.append(advisor)
                         
        if (SEC_DOCTORAL in line) or (SEC_ACADEMIC in line):
            advisor_start = True
            
    return advisors
    
    
    
def process_url(url):
    response = urllib2.urlopen(url)
    page = response.read()
    advisors = get_advisors(page)
    return advisors
    
def get_tree(url, G):
    print 'Processing: ' + url
    current = url.split('/')[-1]
    advisors = process_url(url)
    proccessed.append(current)
    for advisor in advisors:
        name = advisor.split('/')[-1]
        if name in proccessed:
            print 'Already processed: ' + name
            continue
        G.add_edge(name, current)        
        get_tree (BASE_URL + advisor, G)
    
    return G

    

#Usage example
if __name__ == "__main__":   
    G = get_tree('http://en.wikipedia.org/wiki/Andy_Hopper', G)
    print G.nodes()
    nx.write_gexf(G, "./test.gexf")

        