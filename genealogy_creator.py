# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 15:08:25 2013

@author: Aitor
"""

import re
import urllib2
import networkx as nx

BASE_URL = 'http://en.wikipedia.org'

# Advisors appear both as doctoral or academic advisors
SEC_DOC_ADVISOR = '>Doctoral advisor'
SEC_ACA_ADVISOR = '>Academic advisor'
# Students  appear both as doctoral or notable students
SEC_NOT_STUDENTS = '>Notable student'
SEC_DOC_STUDENTS = '>Doctoral student'
SEC_END = '</tr>'

WIKI_PERSON = '\/wiki/\D+\"'

MAX_DEPTH = 6

p = re.compile(WIKI_PERSON)
    
def get_connections(page):
    
    lines = page.split('\n')
    
    advisor_start = False  
    student_start = False  

    advisors = []
    students = []

    for line in lines:
        if advisor_start or student_start:
            if SEC_END in line:
                advisor_start = False  
                student_start = False 
            matches = p.findall(line)
            for m in matches:
                person = m.split('"')[0]
                if advisor_start:
                    advisors.append(person)
                elif student_start:
                    students.append(person)
                         
        if (SEC_DOC_ADVISOR in line) or (SEC_ACA_ADVISOR in line):
            advisor_start = True
        elif (SEC_DOC_STUDENTS in line) or (SEC_NOT_STUDENTS in line):
            student_start = True
            
    return advisors, students
    
    
    
def process_url(url):
    response = urllib2.urlopen(url)
    page = response.read()
    advisors, students = get_connections(page)
    return advisors, students
    
def get_trunk(url, G, processed):
    print 'Processing: ' + url
    current = url.split('/')[-1]
    advisors, _ = process_url(url)
    to_process = []
    processed.append('/wiki/' + current)
    for advisor in advisors:
        name = advisor.split('/')[-1]
        if not G.has_edge(name, current):
            G.add_edge(name, current)
        if not advisor in processed:
            to_process.append(advisor)
        else:
            print 'Already processed: ' + advisor
        
    for person in to_process:   
        if not person in processed:
            _, processed = get_trunk(BASE_URL + person, G, processed)     
        else:
            print 'Already processed: ' + person
    
    return G, processed
    
def expand_tree (G, processed):
    for advisor in G.nodes():
        if not advisor in processed:
            print 'Getting students of: ' + advisor
            _, students = process_url(BASE_URL + '/wiki/' + advisor)
            processed.append(advisor)
            for student in students:
                student_name = student.split('/')[-1]
                if not G.has_edge(advisor, student_name):
                    G.add_edge(advisor, student_name)
        else:
            print 'Already processed: ' + advisor
    return G, processed

def build_genealogy(base_person):
    G = nx.DiGraph()
    processed = []
    G, _ = get_trunk(base_person, G, processed)
    processed = []
    for i in range(MAX_DEPTH):
        print 'Expanding: ' + str(i)
        G, processed = expand_tree(G, processed) 
    return G
    



if __name__ == "__main__":   
    G = build_genealogy('http://en.wikipedia.org/wiki/Andy_Hopper')
    print G.nodes()
    nx.write_gexf(G, "./test.gexf")

         