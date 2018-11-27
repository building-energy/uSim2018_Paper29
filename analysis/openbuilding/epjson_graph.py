# -*- coding: utf-8 -*-

import json

try:
    from .graph import Graph
except ImportError:
    from graph import Graph
    
try:
    from .graph import Node
except ImportError:
    from graph import Node


class EpjsonGraph(Graph):
    """An EnergyPlus JSON (epJSON) graph
    """
    
    def read_epjson(self,fp):
        with open(fp,'r') as f:
            epjson=json.load(f)
        for k,v in epjson.items():
            label=k
            for k1,v1 in v.items():
                n=self.add_node(labels=label)
                n.id=k1
                n.properties.update(v1)
    
    
    def write_epjson(self,fp):
        d={}
        for n in self.nodes:
            label=n.labels[0]
            name=n.id
            fields={}
            for k,v in n.properties.items():
                if not k=='id':
                    fields[k]=v
            if not label in d:
                d[label]={name:fields}
            else:
                d[label][name]=fields
        with open(fp,'w') as f:
            json.dump(d,
                      f,
                      sort_keys=True,
                      indent=4)
        
        
from pprint import pprint
        
if __name__=='__main__':
    print('test-epjson_graph.py')
    
    g=EpjsonGraph()
    
    g.read_epjson(r'../tests/epjson_graph/detached_house.epJSON')
    
    pprint([x[0] for x in g.graph_dict()['nodes'].values()])
    
    g.write_epjson(r'../tests/epjson_graph/test.epJSON')
    g.write_graphml(r'../tests/epjson_graph/test.graphml')
    g.write_json(r'../tests/epjson_graph/test.json')
    g.write_pickle(r'../tests/epjson_graph/test.pickle')