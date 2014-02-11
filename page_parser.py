# -*- coding: utf-8 -*-
"""
Created on Tue Feb 04 09:11:14 2014

@author: aitor
"""

import gzip
import networkx as nx
import re
import glob
from networkx.readwrite import json_graph

ADVISOR_NAME = '\<a href\=\"id.php\?id\=\d+\"\>'
parser_name = re.compile(ADVISOR_NAME)


G = nx.DiGraph()
total_files = len(glob.glob('./data/data/id.php_id_[0-9]*.html.gz'))

i = 0.0

for filename in glob.glob('./data/data/id.php_id_[0-9]*.html.gz'):
    i += 1.0
    f = gzip.open(filename)
    contents = f.read()
    f.close()
    fi = contents.decode('utf-8')
    fi = fi.split('\n')
    
    name = ''
    author_id = str(filename.split('id_')[1].split('.')[0])
    advisors = {}
    for line in fi:
        if '<title>' in line:
            name = line.split(' - ')[1].split('<')[0]
            
        if 'Advisor' in line:
            matches = parser_name.findall(line) 
            current = line
            for match in matches:
                advisor_id = match.split('id=')[1].split('"')[0]
                current = current.split(match)[1]
                advisor_name = current.split('</a>')[0]

                advisors[advisor_id] = advisor_name
    

    author_id = name + author_id
    if not G.has_node(author_id):
        G.add_node(author_id, name = name)
    for advisor in advisors:
        advisor_id = advisors[advisor] + advisor
        if not G.has_node(advisor_id):
            G.add_node(advisor_id, name = advisors[advisor])
        if not G.has_edge(advisor_id, author_id):
            G.add_edge(advisor_id, author_id)     
    
    done = (i/total_files) * 100
    if i%300 == 0:
        print done

print 'Graph created'
print 'Nodes:'   
print len(G.nodes())
print 'Edges:'
print len(G.edges())
print 'Writing file...'
nx.write_gexf(G, './data/genealogy.gexf') 
with open('./data/genealogy.json', 'w') as outfile:
  json_graph.dump(G, outfile)
nx.write_edgelist(G, './data/genealogy.csv')
print 'done'