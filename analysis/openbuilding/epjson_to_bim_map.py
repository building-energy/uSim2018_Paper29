# -*- coding: utf-8 -*-

import pandas as pd

try:
    from .bim_graph import BimGraph
except ImportError:
    from bim_graph import BimGraph
    
try:
    from .schedules import YearSchedule,PeriodSchedule,WeekSchedule,DaySchedule
except ImportError:
    from schedules import YearSchedule,PeriodSchedule,WeekSchedule,DaySchedule
    
class EpjsonToBimMap():
    "A mapping object to transfer gbXML to Bim"
    
    label_dict=\
        {'Building':'Building',
         'Zone':'Space',
         'BuildingSurface:Detailed':'Surface',
         'FenestrationSurface:Detailed':'Opening'
         }
    
    
    
    
    def __init__(self):
        self.input_epjson=None
        self.output_bim=None

    def _map_properties(self,epjson_node,bim_node):
        "Maps the node properties"
        bim_node.properties.update(epjson_node.properties)



    def run(self):
        
        self.output_bim=BimGraph()

        # MAP NODES

        for n in self.input_epjson.nodes:
            label=n.labels[0]
            if label in ['Building',
                         'Zone',
                         'BuildingSurface:Detailed',
                         'FenestrationSurface:Detailed'
                         ]:
                bim_label=EpjsonToBimMap.label_dict[label]
                n1=self.output_bim.add_node(labels=bim_label)
                self._map_properties(n,n1)


if __name__=='__main__':
    from pprint import pprint
    from epjson_graph import EpjsonGraph
    
    # get gbxml
    g=EpjsonGraph()
    g.read_epjson(r'../tests/epjson_to_bim_map/detached_house.epJSON')
    
    # map
    o=EpjsonToBimMap()
    o.input_epjson=g
    o.run()
    bim=o.output_bim
    pprint(bim.graph_dict()['nodes'])
    #print(bim.Building[0]._node_tuple)
    
   
    #print(o.output_bim)
    bim.write_pickle(r'../tests/epjson_to_bim_map/detached_house.pickle')
    bim.write_json(r'../tests/epjson_to_bim_map/detached_house.json')
    bim.write_graphml(r'../tests/epjson_to_bim_map/detached_house.graphml')