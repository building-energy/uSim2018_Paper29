# -*- coding: utf-8 -*-

from opengraph import XmlGraph
from opengraph.xml_node import XmlNode

    
class RefitxmlGraph(XmlGraph):
    """A refitXML graph
    """

    @staticmethod
    def _node(graph,_id,node_tuple):
        """Returns a Node instance
        """
        return RefitxmlNode(graph,_id,node_tuple)
    

class RefitxmlNode(XmlNode):
    "A refitXML node"
    pass
    

    def gas_meters(self):
        "Returns the gas meters of a building node"
        return [n for n in self.Meter if n.attributes['meterType']=='Gas']

# tests    
    
from pprint import pprint
        
if __name__=='__main__':
    print('test-refitxmlgraph.py')
    
    g=RefitxmlGraph()
    g.read_xml(r'../tests/refitxml_graph/REFIT_BUILDING_SURVEY_INTERNAL_170713.xml')
    #print(g.graph_dict())
    print(g.Building[0].attributes['id'])
    
    #import sys
    #sys.setrecursionlimit(10000)
    #g.write_pickle(r'../tests/refitxml_graph/REFIT_BUILDING_SURVEY_INTERNAL_170713.pickle')

    #h=g.copy()
    #print(h.Building[0].attributes['id'])

    g.write_graphml(r'../tests/refitxml_graph/test.graphml')
    g.write_json(r'../tests/refitxml_graph/test.json')
    g.write_pickle(r'../tests/refitxml_graph/test.pickle')

