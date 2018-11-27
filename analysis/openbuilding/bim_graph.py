# -*- coding: utf-8 -*-

try:
    from .graph import Graph
except ImportError:
    from graph import Graph
    
try:
    from .graph import Node
except ImportError:
    from graph import Node

import pandas as pd

class BimGraph(Graph):
    """A Bim graph
    """
    
    
    @staticmethod
    def _node(self,_id,node_tuple):
        "Returns a Node instance"
        return BimNode(self,_id,node_tuple)

    
    

#------------------------------------------------------------------------------
    
class BimNode(Node):
    "A Bim node"


    def add_inner_next_to_edge(self,
                               adjacent_node):
        "Adds an inner edge"
        self._graph.add_edge(self,
                            adjacent_node,
                            'next_to',
                            properties={'type':'inner'}
                            )
        self._graph.add_edge(adjacent_node,
                            self,
                            'next_to'
                            )
    
    
    def add_outer_next_to_edge(self,
                               adjacent_node):
        "Adds an outer edge"
        self._graph.add_edge(self,
                            adjacent_node,
                            'next_to',
                            properties={'type':'outer'}
                            )
        self._graph.add_edge(adjacent_node,
                            self,
                            'next_to'
                            )
    
    def contains(self):
        return self.successor_nodes(name='contains')
    
    
    def environment_surfaces(self):
        "Returns the surfaces adjacent to the environment"
        l=[]
        for surface in self.surfaces:
            if surface.environments:
                l.append(surface)
        return l
    
    
    def external_surfaces(self):
        "Returns the surfaces adjacent to the environment and ground"
        l=[]
        for surface in self.surfaces:
            if surface.environments or surface.grounds:
                l.append(surface)
        return l
    
    
    def ground_surfaces(self):
        "Returns the surfaces adjacent to the ground"
        l=[]
        for surface in self.surfaces:
            if surface.grounds:
                l.append(surface)
        return l
    
    
    def has(self):
        return self.successor_nodes(name='has')
    
    
    def heating_schedule(self):
        "Returns the heating schedule of the node"
        for e in self.out_edges:
            if (e.name=='has' 
                and e.properties.get('type')=='heating'
                and 'Schedule' in e.end_node.labels):
                return e.end_node
        return None
    
    
    def inner_next_to(self):
        "Returns the inner next_to node"
        for e in self.out_edges:
            if e.name=='next_to' and e.properties.get('type')=='inner':
                return e.start_node
        return None
    
    
    def internal_surfaces(self):
        "Returns the surfaces adjacent to another Space"
        l=[]
        for surface in self.surfaces:
            if len(surface.spaces)==2:
                l.append(surface)
        return l
    
    
    def is_contained_by(self):
        return self.predeccessor_nodes(name='contains')
    
    
    def is_haved_by(self):
        return self.predeccessor_nodes(name='has')
    
    
    def Layers(self):
        "Returns the layers for the node, from outer to inner"
        l=[]
        node=self
        while True:
            try:
                layer=node.Layer[0]
            except IndexError:
                return l
            l.append(layer)
            node=layer
        
    
    def next_to(self):
        return self.successor_nodes(name='next_to')
    
    
    def ordered_materials(self):
        "Returns the material nodes for a construction, in order"
        name1='has'
        material_edges=[e for e in self.out_edges
                        if e.name==name1]
        l=[None]*len(material_edges)
        for material_edge in material_edges:
            index=material_edge.properties['index']
            l[index]=material_edge
        l=[e.end_node for e in l]
        return l
    
    
    def outer_next_to(self):
        "Returns the outer next_to node"
        for e in self.out_edges:
            if e.name=='next_to' and e.properties.get('type')=='outer':
                return e.start_node
        return None
    
    
# TESTS
    
if __name__=='__main__':
    from pprint import pprint
    from bim_graph import BimGraph
    import matplotlib.pyplot as plt
    
    print('TEST-BimGraph')
    
    print('TEST-INSTANTIATE GRAPH')
    o=BimGraph()
#    o.read_pickle(r'../tests/bim_graph/detached_house2.pickle')
#    print(o)
#    
#    print('TEST-label_dict_of_nodes')
#    d=o.label_dict_of_ids()
#    pprint(d)
#    
#    space=o.buildings[0].spaces[0]
#    d={}
#    for k,v in space.dfs.items():
#        d[k]=v.sum().iloc[0]/1000000
#    pprint(d)
#    
#    print([n.id1 for n in space.surfaces])
#    print([n.id1 for n in space.external_surfaces])
#    
#    print(o.buildings[0].dfs.keys())
#    
#    print(space.json_dict())
#    
  

#def add_appliance_node(self,
#                           id1=None,
#                           name=None,
#                           heat_gain_per_area=None
#                           ):
#        """
#        Adds an Appliance object to the Bim instance
#        
#        Arguments:
#            n (str): the id string
#            schedule_id (object): a schedule which gives the fraction of heat gains
#            maximum_heat_gain (float): the total heat gains in W
#            links: keywords for the add_links method
#        
#        """
#        labels=['PhysicalObject',
#                'Appliance']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'HeatGainPerArea':heat_gain_per_area
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_building_node(self,
#                          id1=None,
#                          name=None,
#                          CADModelAzimuth=None):
#        "Adds a building node"
#        labels=['PhysicalCollection',
#                'Building']
#        properties={'id':id1,
#                    'Name':name,
#                    'CADModelAzimuth':CADModelAzimuth,
#                    }
#        return self.add_node(labels,properties)
#    
#    
#    def add_construction_node(self,
#                              id1=None,
#                              name=None,
#                              uvalue=None):
#        "Adds a Construction node"
#        labels=['TypeObject',
#                'Construction']
#        properties={'id':id1,
#                    'Name':name,
#                    'Uvalue':uvalue
#                    }
#        return self.add_node(labels,properties)
#    
#    
#    def add_electric_room_heater_node(self,
#                                      id1=None,
#                                      name=None,
#                                      capacity=None,
#                                      ):
#        """
#        Adds an ElectricRoomHeater Node
#        
#        Arguments:
#            capacity (float): the maximum power of the heater in kW
#        """
#        labels=['PhysicalObject',
#                'ElectricRoomHeater']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'Capacity':capacity
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_environment_node(self):
#        "Adds an environment node"
#        return self.add_node(labels=['PhysicalObject','Environment'])
#    
#    
#    def add_glazing_material_node(self,
#                                  id1=None,
#                                  name=None,
#                                  thickness=None,
#                                  solar_transmittance_at_normal_incidence=0.775,
#                                  front_side_solar_reflectance_at_normal_incidence=0.071,
#                                  back_side_solar_reflectance_at_normal_incidence=0.071,
#                                  visible_transmittance_at_normal_incidence=0.881,
#                                  front_side_visible_reflectance_at_normal_incidence=0.080,
#                                  back_side_visible_reflectance_at_normal_incidence=0.080,
#                                  infrared_transmittance_at_normal_incidence=0,
#                                  front_side_infrared_hemispherical_emissivity=0.84,
#                                  back_side_infrared_hemispherical_emissivity=0.84,
#                                  conductivity=0.9
#                                  ):
#        """
#        Adds a GlazingMaterial node
#        """
#        labels=['TypeObject',
#                'GlazingMaterial']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'Thickness':thickness,
#             'solar_transmittance_at_normal_incidence':solar_transmittance_at_normal_incidence,
#             'front_side_solar_reflectance_at_normal_incidence':front_side_solar_reflectance_at_normal_incidence,
#             'back_side_solar_reflectance_at_normal_incidence':back_side_solar_reflectance_at_normal_incidence,
#             'visible_transmittance_at_normal_incidence':visible_transmittance_at_normal_incidence,
#             'front_side_visible_reflectance_at_normal_incidence':front_side_visible_reflectance_at_normal_incidence,
#             'back_side_visible_reflectance_at_normal_incidence':back_side_visible_reflectance_at_normal_incidence,
#             'infrared_transmittance_at_normal_incidence':infrared_transmittance_at_normal_incidence,
#             'front_side_infrared_hemispherical_emissivity':front_side_infrared_hemispherical_emissivity,
#             'back_side_infrared_hemispherical_emissivity':back_side_infrared_hemispherical_emissivity,
#             'conductivity':conductivity
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_glazing_gap_node(self,
#                             id1=None,
#                             name=None,
#                             thickness=None,
#                             gas_type='Air'
#                             ):
#        """
#        Adds a GlazingGap node
#        """
#        labels=['TypeObject',
#                'GlazingGap']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'Thickness':thickness,
#             'GasType':gas_type # one of 'Air', 'Argon', 'Krypton', or 'Xenon'
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_ground_node(self):
#        "Adds a ground node"
#        return self.add_node(labels=['PhysicalObject','Ground'])
#    
#    
#    def add_light_node(self,
#                       id1=None,
#                       name=None,
#                       heat_gain_per_area=None,
#                       ):
#        """
#        Adds a Light object to the Bim instance
#        
#        
#        
#        """
#        labels=['PhysicalObject',
#                'Light']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'HeatGainPerArea':heat_gain_per_area
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_opaque_airgap_node(self,
#                               id1=None,
#                               name=None,
#                               thickness=None,
#                               thermal_resistance=0.18,
#                               ):
#        """
#        Adds an OpaqueAirgap node
#        """
#        labels=['TypeObject',
#                'OpaqueAirGap']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'Thickness':thickness,
#             'ThermalResistance':thermal_resistance
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_opaque_material_node(self,
#                                 id1=None,
#                                 name=None,
#                                 thickness=None,
#                                 roughness='Smooth',
#                                 conductivity=None,
#                                 density=None,
#                                 specific_heat=None,
#                                 thermal_absorptance=0.9,
#                                 solar_absorptance=0.7,
#                                 visible_absorptance=0.9):
#        "Adds a OpaqueMaterial node"
#        labels=['TypeObject',
#                'OpaqueMaterial']
#        properties={'id':id1,
#                    'Name':name,
#                    'Thickness':thickness,
#                    'Roughness':roughness,
#                    'Conductivity':conductivity,
#                    'Density':density,
#                    'SpecificHeat':specific_heat,
#                    'ThermalAbsorptance':thermal_absorptance,
#                    'SolarAbsorptance':solar_absorptance,
#                    'VisibleAbsorptance':visible_absorptance
#                    }
#        return self.add_node(labels,properties)    
#    
#    
#    def add_opening_node(self,
#                         id1=None,
#                         name=None,
#                         openingType=None,
#                         coordinates=None):
#        "Adds an Opening node"
#        labels=['PhysicalObject',
#                'Opening']
#        properties={'id':id1,
#                    'Name':name,
#                    'OpeningType':openingType,
#                    'Coordinates':coordinates
#                    }
#        return self.add_node(labels,properties)
#    
#    
#    def add_people_node(self,
#                        id1=None,
#                        name=None,
#                        number_of_people=None,
#                        person_heat_gain=None,
#                        ):
#        """
#        Adds a People Node
#        
#        Arguments:
#            n (str): the id string
#            number_of_people (float): the number of people
#            person_heat_gain (float): the total heat gains per person in W
#        """
#        labels=['PhysicalObject',
#                'People']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'NumberOfPeople':number_of_people,
#             'PersonHeatGain':person_heat_gain
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_schedule_node(self,
#                          id1=None,
#                          name=None,
#                          year_schedule=None  # a YearSchedule object
#                          ):
#        """
#        Adds a Schedule Node
#        """
#        labels=['TypeObject',
#                'Schedule']
#        properties=\
#            {'id':id1,
#             'Name':name,
#             'YearSchedule':year_schedule
#            }
#        return self.add_node(labels,properties)
#    
#    
#    def add_sensor_node(self):
#        "Adds a sensor node"
#        return self.add_node(labels=['PhysicalObject','Sensor'])
#    
#    
#    def add_space_node(self,
#                       id1=None,
#                       name=None,
#                       area=None,
#                       volume=None,
#                       infiltration_rate=None,  # air changes per hour
#                       condition_type=None
#                       ):
#        "Adds a space node"
#        labels=['PhysicalObject',
#                'Space']
#        properties={'id':id1,
#                    'Name':name,
#                    'Area':area,
#                    'Volume':volume,
#                    'InfiltrationRate':infiltration_rate,
#                    'ConditionType':condition_type
#                    }
#        return self.add_node(labels,properties)
#    
#    
#    def add_surface_node(self,
#                         id1=None,
#                         name=None,
#                         surfaceType=None,
#                         coordinates=None):
#        "Adds a Surface node"
#        labels=['PhysicalObject',
#                'Surface']
#        properties={'id':id1,
#                    'Name':name,
#                    'SurfaceType':surfaceType,
#                    'Coordinates':coordinates
#                    }
#        return self.add_node(labels,properties)
#    
#
#    def environment_surfaces(self):
#        "Returns the surfaces adjacent to the environment"
#        l=[]
#        for surface in self.surfaces:
#            if surface.environments:
#                l.append(surface)
#        return l
#    
#
##    def label_dict_of_nodes(self,
##                           nodes=None):
##        "Returns a dict of {tuple(labels):list of nodes}"
##        if not nodes: nodes=self.nodes
##        d={}
##        for n in nodes:
##            labels=tuple(n.labels)
##            if not labels in d:
##                d[labels]=[n]
##            else:
##                d[labels].append(n)
##        return d
##    
##    def label_dict_of_ids(self,
##                           nodes=None):
##        "Returns a dict of {tuple(labels):list of nodes}"
##        if not nodes: nodes=self.nodes
##        d={}
##        for n in nodes:
##            id1=n.properties.get('id')
##            labels=tuple(n.labels)
##            if not labels in d:
##                d[labels]=[id1]
##            else:
##                d[labels].append(id1)
##        return d