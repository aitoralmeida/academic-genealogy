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

BEGIN_INFOBOX = '<table class="infobox vcard"'
END_INFOBOX = '</table>'

#PERSON_LINK = '\/wiki/\D+\"'
PERSON_LINK = '\<a href\=\"\S+\"'
PERSON_NAME = '\>\D+\<'

MAX_DEPTH = 0

parser_link = re.compile(PERSON_LINK)
parser_name = re.compile(PERSON_NAME)
    
def get_connections(page):
    
    lines = page.split('\n')
    
    advisor_start = False  
    student_start = False 
    infobox_start = False

    advisors = {}
    students = {}

    for line in lines:
        if infobox_start:
            # DOM be dammed (I'm not proud of this :-P)
            if END_INFOBOX in line:
                break
            if advisor_start or student_start:
                if SEC_END in line:
                    advisor_start = False  
                    student_start = False 
                
                matches_links = parser_link.findall(line)   
                name_section = line.split('</a>')[0]
                matches_name = name_section.split('">')[-1]
                if len(matches_links) > 0:
                    person_name = matches_name
                    link_info = matches_links[0]
                    person_link = link_info.split('"')[1]
                    if advisor_start:
                        advisors[person_name] = person_link
                    elif student_start:
                        students[person_name] = person_link
                
#                for m in matches:
#                    person = m.split('"')[0]
#                    if advisor_start:
#                        advisors.append(person)
#                    elif student_start:
#                        students.append(person)
            
                         
        if (SEC_DOC_ADVISOR in line) or (SEC_ACA_ADVISOR in line):
            advisor_start = True
        elif (SEC_DOC_STUDENTS in line) or (SEC_NOT_STUDENTS in line):
            student_start = True
        elif BEGIN_INFOBOX in line:
            infobox_start = True
               
    return advisors, students
    
    
    
def process_url(url):
    try:    
        response = urllib2.urlopen(url)
        page = response.read()
        advisors, students = get_connections(page)
    except urllib2.HTTPError:
        advisors = {}
        students = {}
    return advisors, students
    
def get_trunk(current_name, current_link, G, processed):
    print 'Processing: ' + current_link
    advisors, _ = process_url(current_link)
    to_process = {}
    processed.append(current_link)
    for advisor_name, advisor_link in advisors.items():
        if not G.has_edge(advisor_name, current_name):
            G.add_edge(advisor_name, current_name)
            G.node[advisor_name]['link'] = BASE_URL + advisor_link
            G.node[current_name]['link'] = current_link
        if not advisor_link in processed:
            to_process[advisor_name] = BASE_URL + advisor_link
        else:
            print 'Already processed: ' + advisor_name
        
    for person_name, person_link in to_process.items():   
        if not person_link in processed:
            _, processed = get_trunk(person_name, person_link, G, processed)     
        else:
            print 'Already processed: ' + person_name
    
    return G, processed
    
def expand_tree (G, processed):
    for person in G.nodes():
        if not person in processed:
            print 'Getting relations of: ' + person
            advisors, students = process_url(G.node[person]['link'])
            processed.append(G.node[person]['link'])
            for student_name, student_link in students.items():
                if not G.has_edge(person, student_name):
                    G.add_edge(person, student_name)
                    G.node[student_name]['link'] = BASE_URL + student_link
            for advisor_name, advisor_link in advisors.items():
                if not G.has_edge(advisor_name, person):
                    G.add_edge(advisor_name, person)
                    G.node[advisor_name]['link'] = BASE_URL + advisor_link
        else:
            print 'Already processed: ' + person
    return G, processed

def build_genealogy(base_person_name, base_person_link):
    G = nx.DiGraph()
    processed = []
    G, _ = get_trunk(base_person_name, base_person_link, G, processed)
    processed = []
    for i in range(MAX_DEPTH):
        print 'Expanding: ' + str(i)
        G, processed = expand_tree(G, processed) 
    return G

if __name__ == "__main__": 
    print 'Getting genealogy'
    G = build_genealogy('Andy Hopper', 'http://en.wikipedia.org/wiki/Andy_Hopper')
    print G.nodes()
    print 'Total nodes: '  + str(len(G.nodes()))
    nx.write_gexf(G, "./test.gexf")
    print 'Fin'
    
#    G = nx.read_gexf("./test.gexf")
#    for person in G.nodes():
#        advisors, _ = process_url(BASE_URL + '/wiki/' + person)
#        for advisor in advisors:
#            name = advisor.split('/')[-1]
#            if not G.has_edge(name, person):
#                G.add_edge(name, person)
#                print 'added: ' + name + '-' + person
#    
#    nx.write_gexf(G, "./test.gexf")
            

         