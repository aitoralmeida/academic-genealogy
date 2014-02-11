# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:36:21 2014

@author: aitor
"""

import requests
import networkx as nx


QUERY_ACADEMIC_ADVISOR = '''SELECT ?labelAdvisor ?advisor ?labelStudent ?student  WHERE {
                                 ?student rdfs:label ?labelStudent .
                                 ?student <http://dbpedia.org/ontology/academicAdvisor> ?advisor.
                                 ?advisor rdfs:label ?labelAdvisor .
                                 FILTER (LANG(?labelStudent ) = 'en') .
                                 FILTER (LANG(?labelAdvisor ) = 'en') .
                             }'''
                             
QUERY_DOCTORAL_ADVISOR = '''SELECT ?labelAdvisor ?advisor ?labelStudent ?student  WHERE {
                                 ?student rdfs:label ?labelStudent .
                                 ?student <http://dbpedia.org/ontology/doctoralAdvisor> ?advisor.
                                 ?advisor rdfs:label ?labelAdvisor .
                                 FILTER (LANG(?labelStudent ) = 'en') .
                                 FILTER (LANG(?labelAdvisor ) = 'en') .
                             }'''
                             
QUERY_DOCTORAL_STUDENT = '''SELECT ?labelAdvisor ?advisor ?labelStudent ?student WHERE {
                                 ?advisor rdfs:label ?labelAdvisor.
                                 ?advisor <http://dbpedia.org/ontology/doctoralStudent> ?student.
                                 ?student rdfs:label ?labelStudent.
                                 FILTER (LANG(?labelStudent ) = 'en') 
                                 FILTER (LANG(?labelAdvisor ) = 'en') .
                            }'''
                            
QUERY_NOTABLE_STUDENT = '''SELECT ?labelAdvisor ?advisor ?labelStudent ?student WHERE {
                                 ?advisor rdfs:label ?labelAdvisor.
                                 ?advisor <http://dbpedia.org/ontology/notableStudent> ?student.
                                 ?student rdfs:label ?labelStudent.
                                 FILTER (LANG(?labelStudent ) = 'en') 
                                 FILTER (LANG(?labelAdvisor ) = 'en') .
                            }'''
                             
                             
queries = [QUERY_ACADEMIC_ADVISOR, QUERY_DOCTORAL_ADVISOR, QUERY_DOCTORAL_STUDENT, QUERY_NOTABLE_STUDENT]    

def add_node(G, node, node_label):
    if not G.has_node(node):
        G.add_node(node, name = node_label)
        
def add_edge(G, source, target):
    if not G.has_edge(source, target):
        G.add_edge(source, target)

def scrap_dbpedia():
    G = nx.DiGraph()
    
    for querie in queries:
        print 'Executing querie: ' + querie
        payload = {'query': querie,
                    'format': 'json'}
        r = requests.get("http://dbpedia.org/sparql/", params=payload)
        results = r.json()['results']['bindings']
        for result in results:
            advisor = result['advisor']['value']
            advisorName = result['labelAdvisor']['value']
            student = result['student']['value']
            studentName = result['labelStudent']['value']
            print u'Advisor:', advisor, u'student:', student
            add_node(G, advisor, advisorName)
            add_node(G, student, studentName)
            add_edge(G, advisor, student)
    
    print ''
    print '-Nodes: '
    print len(G.nodes())
    print '-Edges: '
    print len(G.edges())
    print 'Writing file'
    nx.write_gexf(G, 'dbpedia_genealogy.gexf')
    print 'Done'
    
    
if __name__ == '__main__':
    scrap_dbpedia()
        
        
        

    