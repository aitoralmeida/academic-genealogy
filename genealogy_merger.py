# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 14:54:32 2014

@author: aitor
"""

import networkx as nx
import json



def load_graphs(dbpedia_path = 'dbpedia_genealogy.gexf', math_path = 'math_genealogy.gexf'):
    dbpedia = nx.read_gexf(dbpedia_path)

    math = nx.read_gexf(math_path, node_type = None)
    
    return dbpedia, math

#should be run once to create the indexes, it takes its time (at least 30 min)
def create_inverse_indexes():
    dbpedia, math = load_graphs()
    dbpedia_inverse_index = {}
    total = len(dbpedia.nodes())
    print 'Dbpedia nodes to process:',total
    for i, node in enumerate(dbpedia.nodes()):
        if i%500 == 0:
            print 'dbpedia: ', (float(i)/float(total))*100
        node_id = node
        node_name = dbpedia.node[node]['name']
        if node_name in dbpedia_inverse_index.keys():
            dbpedia_inverse_index[node_name].append(node_id)
        else:
            dbpedia_inverse_index[node_name] = [node_id]
    
    with open('index_dbpedia.json', 'w') as outfile:
        json.dump(dbpedia_inverse_index, outfile)
            
    print u'Created dbpedia reverse index:', len(dbpedia_inverse_index)
            
    math_inverse_index = {}
    total = len(math.nodes())
    print 'Math nodes to process:',total
    for i, node in enumerate(math.nodes()):
        if i%500 == 0:
            print 'math:',(float(i)/float(total))*100
        node_id = node
        node_name = math.node[node]['name']
        if node_name in math_inverse_index.keys():
            math_inverse_index[node_name].append(node_id)
        else:
            math_inverse_index[node_name] = [node_id]
    
    with open('index_math.json', 'w') as outfile:
        json.dump(math_inverse_index, outfile)
        
    print u'Created math reverse index:', len(math_inverse_index)
 
#also should be run once to create the index   
def create_edge_index():
    print 'Loading graphs'
    dbpedia, math = load_graphs()
    print 'Creating edge index'
    dict_edges = {}
    total = len(math.edges())
    for i, edge in enumerate(math.edges()):
        if i%500 == 0:
            print 'edge index:',(float(i)/float(total))*100
        source = edge[0]
        target = edge[1]
        if target in dict_edges.keys():
            dict_edges[target] = dict_edges[target] + [source]
        else:
            dict_edges[target] = [source]    
            
    with open('index_edges.json', 'w') as outfile:
        json.dump(dict_edges, outfile)
    
    print u'Created edge index:', len(dict_edges)
    
def create_merged_edge_index():
    print 'Loading graph'
    merged = nx.read_gexf('merged_genealogy.gexf', node_type = None)
    print 'Creating edge index'
    dict_edges = {}
    total = len(merged.edges())
    for i, edge in enumerate(merged.edges()):
        if i%500 == 0:
            print 'edge index:',(float(i)/float(total))*100
        source = edge[0]
        target = edge[1]
        if target in dict_edges.keys():
            dict_edges[target] = dict_edges[target] + [source]
        else:
            dict_edges[target] = [source]    
            
    with open('index_merged_edges.json', 'w') as outfile:
        json.dump(dict_edges, outfile)
    
    print u'Created merged edge index:', len(dict_edges)
    
def load_inverse_indexes():
    with open('index_dbpedia.json', 'r') as infile:
        dbpedia_inverse_index =  json.load(infile)
    with open('index_math.json', 'r') as infile:
        math_inverse_index =  json.load(infile)
        
    return dbpedia_inverse_index, math_inverse_index
    
def load_edge_index():
    with open('index_edges.json', 'r') as infile:
        edge_index =  json.load(infile)
    
    return edge_index
    
def load_merged_edge_index():
    with open('index_merged_edges.json', 'r') as infile:
        edge_index =  json.load(infile)
    
    return edge_index

def merge_datasets():  
    print 'Loading indexes'
    dbpedia_inverse_index, math_inverse_index = load_inverse_indexes()
    print 'Loading graphs'
    dbpedia, math = load_graphs()         
    equivalent_ids = {}
    
    print 'Procesing nodes'
    existing_nodes = 0
    new_nodes = 0
    print 'Total nodes: ', len(dbpedia.nodes())
    for i, node in enumerate(dbpedia.nodes()):
        
        name = dbpedia.node[node]['name']
        if name in math_inverse_index.keys():
            equivalent_ids[node] = math_inverse_index[name]
            existing_nodes += 1
        else:     
            math.add_node(node, name=name)
            new_nodes += 1

    print 'Existing nodes', existing_nodes
    print 'New nodes', new_nodes
    
    print 'Procesing edges' 
    print 'Total edges: ', len(dbpedia.edges())       
    for edge in dbpedia.edges():
        source = edge[0]
        target = edge[1]
        
        if source in equivalent_ids.keys():
            for eq_source in equivalent_ids[source]:
                if target in equivalent_ids.keys():
                    for eq_target in equivalent_ids[target]:
                        math.add_edge(eq_source,eq_target)
                else:
                    math.add_edge(eq_source,target)
        else:
            if target in equivalent_ids.keys():
                for eq_target in equivalent_ids[target]:
                    math.add_edge(source,eq_target)
            else:
                math.add_edge(source,target)
    print 'Final graph'
    print '-nodes: ', len(math.nodes())
    print '-edges: ', len(math.edges())         
    print 'Writing file'  
    nx.write_gexf(math, 'merged_genealogy.gexf')
                        




def create_genealogy(graph_id = 'deusto.aitoralmeida'):
    print 'Loading graph'
    merged = nx.read_gexf('merged_genealogy.gexf', node_type = None)
    print 'Loading edge index'
    dict_edges = load_merged_edge_index()
    
    print 'Building genealogy'
    to_process = [graph_id]
    tree = set()
    #get all the ascenstors in tree
    while len(to_process) > 0:
        current = to_process[0]
        to_process.remove(current)
        tree.add(current) 
        
        try:
            to_process += dict_edges[current]
        except:
            pass 
        
    print 'Creating graph'
    G = nx.DiGraph()
    for person in tree:
        print person
        G.add_node(person, name = merged.node[person]['name'])
        for target in merged.edge[person].keys(): 
            #add edges with the ancestors only       
            if target in tree:        
                G.add_edge(person, target)
    print 'Writing file'
    nx.write_gexf(G, 'created_genealogy.gexf')    

            

if __name__=='__main__':
    create_genealogy()
    print 'done'

