# -*- coding: utf-8 -*-

import copy
import sys
import pandas as pd

try:
    from .bim_graph import BimGraph
except ImportError:
    from bim_graph import BimGraph
    
try:
    from .timeseries import Variable
except ImportError:
    from timeseries import Variable

class EsoToBimMap():
    """A mapping object to transfer EsoGraph to BimGraph
    
    This requires an input bim object, and the data in the EsoGraph is
        incorporated into this BimGraph based on the node property ids
        
    ONLY WORKS IF THE ESO VARIABLE HAS BEEN LISTED IN ONE OF THE 'map_dicts' BELOW
    
    """
    
    def __init__(self):
        self.input_eso=None
        self.bim=None
    

    def _find_bim_node(self,eso_node):
        "Returns the Bim node that matches eso_node label"
        # id of eso node
        id1=eso_node.labels[0]
                
        # environment
        if id1=='Environment':
            return self.bim.Climate[0]
        # building
        if id1.startswith('Whole Building'):
            return self.bim.Building[0]
        
        # baseboard heat
        if id1.endswith('BASEBOARD HEAT'):
            space_id=id1[:-len(' BASEBOARD HEAT')]
            space_node=self.bim.filter_node_by_property(key='id',
                                                        value=space_id)
            electric_room_heater_node=\
                space_node.RoomHeater[0]
            return electric_room_heater_node
        
        # all other nodes
        else:
            return self.bim.filter_node_by_property(key='id',
                                                    value=id1)
    
    
    def _map_building(self,bim_node,eso_node):
        ""
        map_dict=\
            {'Facility Total Building Electric Demand Power':'electric_power'}
        variable_name=map_dict[eso_node.properties['variable_name']]
        self._map_node(bim_node,eso_node,variable_name)
                    
    
    def _map_environment(self,bim_node,eso_node):
        ""
        map_dict=\
            {'Site Outdoor Air Drybulb Temperature':'air_drybulb_temperature',
             'Site Diffuse Solar Radiation Rate per Area':'diffuse_solar_radiation',
             'Site Direct Solar Radiation Rate per Area':'direct_solar_radiation',
             'Site Surface Ground Temperature':'surface_ground_temperature',
             }
        variable_name=map_dict[eso_node.properties['variable_name']]
        self._map_node(bim_node,eso_node,variable_name)
    
    
    def _map_node(self,
                 bim_node,
                 eso_node,
                 variable_name):
        "Maps the properties from eso to bim"
        ts=copy.deepcopy(eso_node.properties['ts'])
        units=eso_node.properties['units']  
        var=Variable(name=variable_name,
                     ts=ts,
                     units=units)
        setattr(bim_node,variable_name,var)      
        
        
    def _map_roomHeater(self,bim_node,eso_node):
        ""
        map_dict=\
            {'Baseboard Total Heating Energy':'heating_energy',
             'Baseboard Electric Energy':'electric_energy'
             }
        variable_name=map_dict[eso_node.properties['variable_name']]
        self._map_node(bim_node,eso_node,variable_name)
    
    
    def _map_space(self,bim_node,eso_node):
        ""
        map_dict=\
            {'Zone Total Internal Total Heating Energy':'internal_heat_gain',
             'Zone People Total Heating Energy':'people_heat_gain',
             'Zone Lights Total Heating Energy':'light_heat_gain',
             'Zone Electric Equipment Total Heating Energy':'appliance_heat_gain',
             'Zone Windows Total Transmitted Solar Radiation Energy':'solar_gain',
             'Zone Windows Total Heat Gain Energy':'windows_heat_gain',
             'Zone Windows Total Heat Loss Energy':'windows_heat_loss',
             'Zone Mean Air Temperature':'air_temperature',
             'Zone Infiltration Total Heat Loss Energy':'infiltration_heat_loss',
             'Zone Infiltration Total Heat Gain Energy':'infiltration_heat_gain',
             'Zone Thermostat Heating Setpoint Temperature':'thermostat_setpoint'
             }
        variable_name=map_dict[eso_node.properties['variable_name']]
        self._map_node(bim_node,eso_node,variable_name)
        
        
    def _map_surface(self,bim_node,eso_node):
        ""
        map_dict=\
            {'Surface Inside Face Conduction Heat Transfer Energy':'inside_conduction'
             }
        variable_name=map_dict[eso_node.properties['variable_name']]
        self._map_node(bim_node,eso_node,variable_name)
        
    
    def run(self):
        "Running the mapping, Bim object placed in self.output"
        
        #MAP OBJECTS
        for eso_node in self.input_eso.nodes:
            #FIND BIM NODE TO MAP TO
            bim_node=self._find_bim_node(eso_node)
            if not bim_node: continue
            #MAP
            if 'Climate' in bim_node.labels:
                self._map_environment(bim_node,eso_node)
            elif 'Building' in bim_node.labels:
                self._map_building(bim_node,eso_node)
            elif 'Space' in bim_node.labels:
                self._map_space(bim_node,eso_node)
            elif 'Surface' in bim_node.labels:
                self._map_surface(bim_node,eso_node)
            elif 'RoomHeater' in bim_node.labels:
                self._map_roomHeater(bim_node,eso_node)
        
                
# tests

if __name__=='__main__':
    from pprint import pprint
    from eso_graph import EsoGraph
    from bim_graph import BimGraph
    
    print('TEST-EsoToBimMap.py')
    
    eso=EsoGraph()
    eso.read_eso(r'../tests/eso_to_bim_map/eplusout.eso')
    
    bim=BimGraph()
    bim.read_pickle(r'../tests/eso_to_bim_map/detached_house.pickle')
    
    o=EsoToBimMap()
    o.input_eso=eso
    o.bim=bim
    o.run()
    pprint(o.bim.Climate[0].properties)
    pprint(o.bim.Space[0].properties)
    o.bim.write_pickle(r'../tests/eso_to_bim_map/detached_house_with_eso.pickle')
