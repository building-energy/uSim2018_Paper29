# -*- coding: utf-8 -*-

from graph import Graph

g=Graph()

#NODES

d={
    'Appliance':{
            'doc':"An appliance",
            'properties':{
                    'power_per_area':{
                            'type':'float',
                            'doc':"The electric power per area",
                            'units':'W/m2'
                            }
                    }
            },
    'Building':{
            'doc':"A building",
            'properties':{
                    'orientation':{
                            'type':'float',
                            'doc':"Orientation of the building's coordinate system from due North",
                            'units':'degrees'
                            },
                    'origin_vertex':{
                            'type':'list',
                            'doc':"""The vertex of the origin of the building's coordinate system. 
                                     This is described as [x,y,z]. 
                                     This is relative to the position given in the location. """,
                            'units':'degrees'
                            }
                    }
            },
    'Construction':{
            'doc':"The construction of a surface or opening",
            'properties':{
                    'uvalue':{
                            'type':'float',
                            'doc':"The U-value of the construction",
                            'units':'W/m2K'
                            },
                    }
            },
    'Climate':{
            'doc':"The climate at a location",
            'properties':{
                    }
            },
    'Ground':{
            'doc':"The ground at a location",
            'properties':{
                    }
            },
    'Layer':{
            'doc':"A layer of a construction",
            'properties':{
                    'thickness':{
                            'type':'float',
                            'doc':"The U-value of the construction",
                            'units':'W/m2K'
                            },
                    }
            },
    'LayerElement':{
            'doc':"An element of material within a layer",
            'properties':{
                    'proportion':{
                            'type':'float',
                            'doc':"The proportion of the element in the layer",
                            'units':''
                            },
                    }
            },
    'Light':{
            'doc':"A light",
            'properties':{
                    'power_per_area':{
                            'type':'float',
                            'doc':"The electric power per area",
                            'units':'W/m2'
                            }
                    }
            },
    'Location':{
            'doc':"",
            'properties':{
                    'longitude':{
                            'type':'float',
                            'doc':"",
                            'units':'degrees'
                            },
                    'latitude':{
                            'type':'float',
                            'doc':"",
                            'units':'degrees'
                            }
                    }
            },
    'Opening':{
            'doc':"An opening such as a window or door",
            'properties':{
                    'outer_vertices':{
                            'type':'list',
                            'doc':"List of surface vertices; each vertice is described as a [x,y,z] list",
                            'units':'m'
                            },
                    'hole_vertices':{
                            'type':'list',
                            'doc':"List of hole vertices; each vertice is described as a [x,y,z] list",
                            'units':'m'
                            },
                     'area':{
                            'type':'float',
                            'doc':"The cross-sectional area of the surface",
                            'units':'m2'
                            },   
                    }
            },
    'Material':{
            'doc':"A material",
            'properties':{
                    'conductivity':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'density':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'roughness':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'solar_absorptance':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'specific_heat':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'thermal_absorptance':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'visible_absorptance':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            }
                    }
            },
    'MaterialAirGap':{
            'doc':"An air gap in an opaque construction",
            'properties':{
                    'thermal_resistance':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            }
                    }
            },
    'People':{
            'doc':"The people in a Space",
            'properties':{
                    'number_of_people':{
                            'type':'float',
                            'doc':"The number of people in the space",
                            'units':'W'
                            },
                    'heat_gain_per_person':{
                            'type':'float',
                            'doc':"The heat gain per person",
                            'units':'W/person'
                            }
                    }
            },
    'RoomHeater':{
            'doc':"A room heater",
            'properties':{
                    'capacity':{
                            'type':'float',
                            'doc':"The rated capacity of the heater, i.e. it's maximum power",
                            'units':'W'
                            },
                    'fuel_type':{
                            'type':'str',
                            'doc':"",
                            'enum':[
                                    'electricity',
                                    'gas'
                                    ]
                            }
                    }
            },
    'Schedule':{
            'doc':"A schedule",
            'properties':{
                    'year_schedule':{
                            'type':'openbuilding.YearSchedule',
                            'doc':"A YearSchedule object",
                            'units':''
                            }
                    }
            },
    'Sensor':{
            'doc':"A sensor",
            'properties':{
                    }
            },
    'Space':{
            'doc':"A space or room",
            'properties':{
                    'area':{
                            'type':'float',
                            'doc':"The floor area of the space",
                            'units':'m2'
                            },
                    'infiltration':{
                            'type':'float',
                            'doc':"The infiltration of the space, in air changes per hour",
                            'units':'ach'
                            },        
                    'volume':{
                            'type':'float',
                            'doc':"The volume of the space",
                            'units':'m3'
                            }
                    }
            },
    'Surface':{
            'doc':"A surface such as a wall, roof, floor or ceiling",
            'properties':{
                    'outer_vertices':{
                            'type':'list',
                            'doc':"List of surface vertices; each vertice is described as a [x,y,z] list",
                            'units':'m'
                            },
                    'hole_vertices':{
                            'type':'list',
                            'doc':"List of hole vertices; each vertice is described as a [x,y,z] list",
                            'units':'m'
                            },
                     'area':{
                            'type':'float',
                            'doc':"The cross-sectional area of the surface",
                            'units':'m2'
                            },   
                    }
            },
    'WindowMaterialGas':{
            'doc':"An gas gap in an window construction",
            'properties':{
                    'gas_type':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            }
                    }
            },
    'WindowMaterialGlazing':{
            'doc':"A window material",
            'properties':{
                    'back_side_infrared_hemispherical_emissivity':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'back_side_solar_reflectance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'back_side_visible_reflectance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'conductivity':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },        
                    'dirt_correction_factor_for_solar_and_visible_transmittance':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'front_side_infrared_hemispherical_emissivity':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'front_side_solar_reflectance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'front_side_visible_reflectance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'infrared_transmittance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'optical_data_type':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'poisson_s_ratio':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'solar_diffusing':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'solar_transmittance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'thickness':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'visible_transmittance_at_normal_incidence':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    'young_s_modulus':{
                            'type':'float',
                            'doc':"",
                            'units':''
                            },
                    }
            }
  }   
   

for k,v in d.items():
    g.add_node(labels=k,
               properties=v)

#EDGES   

l=[
    [
         g.Appliance[0],
         g.Schedule[0],
         'has_fraction_schedule',
         {
                 'doc':"People-Appliance edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Building[0],
         g.Sensor[0],
         'has_sensor',
         {
                 'doc':"Building-Sensor edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Building[0],
         g.Space[0],
         'contains',
         {
                 'doc':"Building-Space edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Building[0],
         g.Surface[0],
         'contains',
         {
                 'doc':"Building-Surface edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Construction[0],
         g.Layer[0],
         'outer_layer',
         {
                 'doc':"Construction-Layer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Climate[0],
         g.Sensor[0],
         'has_sensor',
         {
                 'doc':"Climate-Sensor edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Climate[0],
         g.Surface[0],
         'next_to',
         {
                 'doc':"Climate-Surface edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':2
                         }  
         }
    ],
    [
         g.Ground[0],
         g.Surface[0],
         'next_to',
         {
                 'doc':"Ground-Surface edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':2
                         }  
         }
    ],
    [
         g.Layer[0],
         g.Layer[0],
         'next_layer',
         {
                 'doc':"Layer-Layer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Layer[0],
         g.LayerElement[0],
         'contains',
         {
                 'doc':"Layer-LayerElement edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.LayerElement[0],
         g.Material[0],
         'has',
         {
                 'doc':"LayerElement-Material edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.LayerElement[0],
         g.MaterialAirGap[0],
         'has',
         {
                 'doc':"LayerElement-MaterialAirGap edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.LayerElement[0],
         g.WindowMaterialGas[0],
         'has',
         {
                 'doc':"LayerElement-WindowMaterialGas edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.LayerElement[0],
         g.WindowMaterialGlazing[0],
         'has',
         {
                 'doc':"LayerElement-WindowMaterialGlazing edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Light[0],
         g.Schedule[0],
         'has_fraction_schedule',
         {
                 'doc':"Light-Schedule edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Location[0],
         g.Building[0],
         'contains',
         {
                 'doc':"Location-Building edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Location[0],
         g.Climate[0],
         'contains',
         {
                 'doc':"Location-Climate edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Location[0],
         g.Ground[0],
         'contains',
         {
                 'doc':"Location-Ground edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Opening[0],
         g.Construction[0],
         'has_construction',
         {
                 'doc':"Opening-Construction edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.People[0],
         g.Schedule[0],
         'has_fraction_schedule',
         {
                 'doc':"People-Schedule edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.RoomHeater[0],
         g.Schedule[0],
         'has_heating_schedule',
         {
                 'doc':"RoomHeater-Schedule heating edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
                        [
         g.RoomHeater[0],
         g.Schedule[0],
         'has_timer_schedule',
         {
                 'doc':"RoomHeater-Schedule timer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Space[0],
         g.Appliance[0],
         'has_appliance',
         {
                 'doc':"Space-Appliance edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Space[0],
         g.Light[0],
         'has_light',
         {
                 'doc':"Space-Light edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Space[0],
         g.People[0],
         'has_people',
         {
                 'doc':"Space-People edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Space[0],
         g.RoomHeater[0],
         'contains',
         {
                 'doc':"Space-RoomHeater edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':1
                         }  
         }
    ],
    [
         g.Space[0],
         g.Sensor[0],
         'has_sensor',
         {
                 'doc':"Space-Sensor edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Space[0],
         g.Surface[0],
         'next_to',
         {
                 'doc':"Space-Surface edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':0,
                         'max':2
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Climate[0],
         'inner_next_to',
         {
                 'doc':"Surface-Climate inner edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Climate[0],
         'outer_next_to',
         {
                 'doc':"Surface-Climate outer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Construction[0],
         'has_construction',
         {
                 'doc':"Surface-Construction edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Ground[0],
         'inner_next_to',
         {
                 'doc':"Surface-Ground inner edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Ground[0],
         'outer_next_to',
         {
                 'doc':"Surface-Ground outer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Opening[0],
         'contains',
         {
                 'doc':"Surface-Opening edge",
                 'from_node':{
                         'min':0,
                         'max':None
                         },
                 'to_node':{
                         'min':1,
                         'max':1
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Space[0],
         'inner_next_to',
         {
                 'doc':"Surface-Space inner edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ],
    [
         g.Surface[0],
         g.Space[0],
         'outer_next_to',
         {
                 'doc':"Surface-Space outer edge",
                 'from_node':{
                         'min':0,
                         'max':1
                         },
                 'to_node':{
                         'min':0,
                         'max':None
                         }  
         }
    ]
  ]

for i in l:
    g.add_edge(start_node=i[0],
               end_node=i[1],
               name=i[2],
               properties=i[3])
    
    

bim_graph_schema=g


from pprint import pprint
pprint(g.graph_dict())



