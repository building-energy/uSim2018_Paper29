# -*- coding: utf-8 -*-

try:
    from .epjson_graph import EpjsonGraph
except ImportError:
    from epjson_graph import EpjsonGraph
    
class BimToEpjsonMap():
    "A mapping object to transfer BimGraph to IdfGraph"
    
    def __init__(self):
        
        input_epjson=EpjsonGraph()
        input_epjson.add_node(labels='Version',
                              properties={'id':'Version 1',
                                          'version_identifier':'8.9'})
        input_epjson.add_node(labels='Timestep',
                              properties={'id':'Timestep 1',
                                          'number_of_timesteps_per_hour':6})
        input_epjson.add_node(labels='GlobalGeometryRules',
                              properties={'id':'GlobalGeometryRules 1',
                                          "coordinate_system": "Relative",
                                          "daylighting_reference_point_coordinate_system": "Relative",
                                          "rectangular_surface_coordinate_system": "Relative",
                                          "starting_vertex_position": "UpperLeftCorner",
                                          "vertex_entry_direction": "Counterclockwise"})
        input_epjson.add_node(labels='RunPeriod',
                              properties={'id':'RunPeriod 1',
                                          "apply_weekend_holiday_rule": "No",
                                          "begin_day_of_month": 1,
                                          "begin_month": 1,
                                          "day_of_week_for_start_day": "Sunday",
                                          "end_day_of_month": 31,
                                          "end_month": 12,
                                          "increment_day_of_week_on_repeat": "Yes",
                                          "number_of_times_runperiod_to_be_repeated": 1,
                                          "start_year": 2001,
                                          "use_weather_file_daylight_saving_period": "No",
                                          "use_weather_file_holidays_and_special_days": "No",
                                          "use_weather_file_rain_indicators": "No",
                                          "use_weather_file_snow_indicators": "No"})
        input_epjson.add_node(labels='Site:GroundTemperature:BuildingSurface',
                              properties={'id':'Site:GroundTemperature:BuildingSurface 1',
                                          "april_ground_temperature": 18.0,
                                          "august_ground_temperature": 18.0,
                                          "december_ground_temperature": 18.0,
                                          "february_ground_temperature": 18.0,
                                          "january_ground_temperature": 18.0,
                                          "july_ground_temperature": 18.0,
                                          "june_ground_temperature": 18.0,
                                          "march_ground_temperature": 18.0,
                                          "may_ground_temperature": 18.0,
                                          "november_ground_temperature": 18.0,
                                          "october_ground_temperature": 18.0,
                                          "september_ground_temperature": 18.0})
        input_epjson.add_node(labels="SimulationControl",
                              properties={'id':"SimulationControl 1", 
                                            "do_plant_sizing_calculation": "No",
                                            "do_system_sizing_calculation": "No",
                                            "do_zone_sizing_calculation": "No",
                                            "run_simulation_for_sizing_periods": "No",
                                            "run_simulation_for_weather_file_run_periods": "Yes"
                                            })
        input_epjson.add_node(labels='Output:VariableDictionary',
                              properties={'id':'Output:VariableDictionary 1',
                                          "key_field": "IDF"})
        input_epjson.add_node(labels='Output:Variable',
                              properties={'id':'Output:Variable 1',
                                          "key_value": "*",
                                          "reporting_frequency": "Hourly",
                                          "variable_name": "Site Outdoor Air Drybulb Temperature"})
        input_epjson.add_node(labels='Output:Variable',
                              properties={'id':'Output:Variable 2',
                                          "key_value": "*",
                                          "reporting_frequency": "Hourly",
                                          "variable_name": "Zone Mean Air Temperature"})
        
        
        self.input_bim=None
        self.input_epjson=input_epjson
        self.output_epjson=None
    
   
    def _map_appliance_node(self,node):
        """
        Adds a ElectricEquipment node 
        """
        name=node.id
        space_node=node.predeccessor_node(label='Space')
        zone_name=space_node.id
        schedule=node.successor_node(name='has_fraction_schedule')
        schedule_name=schedule.id
        heat_gain_per_area=node.power_per_area
        #add Node
        n=self.output_epjson.add_node(
                labels='ElectricEquipment',
                properties={
                        'id':name,
                        "design_level_calculation_method": "Watts/Area",
                        "schedule_name": schedule_name,
                        "watts_per_zone_floor_area": heat_gain_per_area,
                        "zone_or_zonelist_name": zone_name
                        }
                )
                   
        return n
    
    
    def _map_building_node(self,node):
        """
        Adds a Building 
        """
        name=node.id
        north_axis=node.orientation
        n=self.output_epjson.add_node(
                labels='Building',
                properties={
                        'id':name,
                        "loads_convergence_tolerance_value": 0.04,
                        "maximum_number_of_warmup_days": 25,
                        "minimum_number_of_warmup_days": 6,
                        "north_axis": north_axis,
                        "solar_distribution": "FullExterior",
                        "temperature_convergence_tolerance_value": 0.4,
                        "terrain": "Suburbs"
                        }
                )
                
        return n
    
    
    def _map_construction_node(self,node):
        """
        Adds a Construction node 
        """
        name=node.id
        n=self.output_epjson.add_node(
                labels='Construction',
                properties={
                        'id':name
                        }
                )
        layers=node.Layers()
        for i,layer in enumerate(layers):
            if i==0:
                n.properties['outside_layer']=layer.id
            else:
                n.properties['layer_{}'.format(i+1)]=layer.id
            
        return n

    
    def _map_infiltration_node(self,node):
        """
        Adds a ZoneInfiltration:DesignFlowRate node 
        """
        zone_name=node.id
        name=zone_name+'_infiltration'
        air_changes_per_hour=float(node.infiltration)
        if not air_changes_per_hour: return
        
        #add constant schedule
        schedule_name=name+'_schedule'
        self.output_epjson.add_node(
                labels='Schedule:Constant',
                properties={
                        'id':schedule_name,
                        'hourly_value':1
                        }
                )
                                              
        #add node
        n=self.output_epjson.add_node(
                labels='ZoneInfiltration:DesignFlowRate',
                properties={
                        'id':name,
                        "air_changes_per_hour": air_changes_per_hour,
                        "design_flow_rate_calculation_method": "AirChanges/Hour",
                        "schedule_name": schedule_name,
                        "zone_or_zonelist_name": zone_name
                        }
                )
        return n
        
        
    def _map_light_node(self,node):
        """
        Adds a Lights node 
        """
        name=node.id
        space_node=node.predeccessor_node(label='Space')
        zone_name=space_node.id
        schedule=node.successor_node(name='has_fraction_schedule')
        schedule_name=schedule.id
        heat_gain_per_area=node.power_per_area
        #add Node
        n=self.output_epjson.add_node(
                labels='Light',
                properties={
                        'id':name,
                        "design_level_calculation_method": "Watts/Area",
                        "schedule_name": schedule_name,
                        "watts_per_zone_floor_area": heat_gain_per_area,
                        "zone_or_zonelist_name": zone_name
                        }
                )
                   
        return n
    
   
    def _map_material_node(self,node):
        """
        Adds a Material node 
        """
        layer_element=node.predeccessor_node(label='LayerElement')
        layer=layer_element.predeccessor_node(label='Layer')
        name=layer.id
        n=self.output_epjson.add_node(
                labels='Material',
                properties={
                        'id':name,
                        "conductivity": node.conductivity,
                        "density": node.density,
                        "roughness": node.roughness or "Smooth",
                        "solar_absorptance": node.solar_absorptance or 0.7,
                        "specific_heat": node.specific_heat,
                        "thermal_absorptance": node.thermal_absorptance or 0.9,
                        "thickness": layer.thickness,
                        "visible_absorptance": node.visible_absorptance or 0.9
                        }
                )
        return n
        
    
    def _map_material_air_gap_node(self,node):
        """
        Adds a 'Material:AirGap' node 
        """
        layer_element=node.predeccessor_node(label='LayerElement')
        layer=layer_element.predeccessor_node(label='Layer')
        name=layer.id
        n=self.output_epjson.add_node(
                labels='Material:AirGap',
                properties={
                        'id':name,
                        "thermal_resistance":node.thermal_resistance or 0.18
                        }
                )
        return n
  

    def _map_opening_node(self,node):
        """
        Adds a 'FenestrationSurface:Detailed' node 
        """
        #set up
        opening_type_map={'FixedWindow':'Window',
                          'NonSlidingDoor':'Door',
                          'Air':'Air'}
        #name
        name=node.id
        #surface_type
        a=node.openingType
        surface_type=opening_type_map[a]
        #construction_name
        construction_node=node.Construction[0]
        construction_name=construction_node.id
        #building_surface_name
        surface_node=node.predeccessor_node(label='Surface',
                                            name='contains')
        building_surface_name=surface_node.id
        #vertices
        vertices=[]
        for i,x in enumerate(node.outer_vertices):
            vertices.append(("vertex_{}_x_coordinate".format(i+1),x[0]))
            vertices.append(("vertex_{}_y_coordinate".format(i+1),x[1]))
            vertices.append(("vertex_{}_z_coordinate".format(i+1),x[2]))
        #number_of_vertices
        number_of_vertices=len(node.outer_vertices)
        #add node
        n=self.output_epjson.add_node(
                labels='FenestrationSurface:Detailed',
                properties={
                        'id':name,
                        "building_surface_name": building_surface_name,
                        "construction_name": construction_name,
                        "multiplier": 1,
                        "number_of_vertices": number_of_vertices,
                        #"surface_type": "Window",
                        "view_factor_to_ground": "Autocalculate"
                        }
                )
        for x in vertices:
            n.properties[x[0]]=x[1]
        
        return n
    
    
    def _map_people_node(self,node):
        """
        Adds a People node 
        """
        name=node.id
        space_node=node.predeccessor_node(label='Space')
        zone_name=space_node.id
        number_of_people_schedule=node.successor_node(name='has_fraction_schedule')
        number_of_people_schedule_name=\
            number_of_people_schedule.id
        number_of_people=node.number_of_people
        activity_level_schedule_name=name+'_activity_level'
        #add activity schedule node
        person_heat_gain=node.heat_gain_per_person
        self.output_epjson.add_node(
                labels='Schedule:Constant',
                properties={
                        'id':activity_level_schedule_name,
                        'hourly_value':person_heat_gain
                        }
                )
        #add People Node
        n=self.output_epjson.add_node(
                labels='People',
                properties={
                        'id':name,
                        "activity_level_schedule_name": activity_level_schedule_name,
                        "fraction_radiant": node.fraction_radiant or 0.3,
                        "number_of_people": number_of_people,
                        "number_of_people_calculation_method": "People",
                        "number_of_people_schedule_name": number_of_people_schedule_name,
                        "sensible_heat_fraction": "Autocalculate",
                        "zone_or_zonelist_name": zone_name
                        }
                )
        return n
    
    
    def _map_room_heater_node(self,node):
        """
        Adds a 'HVACTemplate:Zone:BaseboardHeat' node to the IdfGraph
        
        Also adds an associated 'HVACTemplate:Thermostat' node
        
        """
        #name
        name=node.id
        #zone_name
        space=node.predeccessor_node(label='Space',
                                     name='contains')
        zone_name=space.id
        #template_thermostat_name
        print(name)
        template_thermostat_name=name+'_thermostat'
        #baseboard_heating_capacity
        baseboard_heating_capacity=node.capacity
        baseboard_heating_type=node.fuel_type
        #add 'HVACTemplate:Zone:BaseboardHeat' node
        self.output_epjson.add_node(
                labels='HVACTemplate:Zone:BaseboardHeat',
                properties={
                        'id':name,
                        'zone_name':zone_name,
                        'template_thermostat_name':template_thermostat_name,
                        'zone_heating_sizing_factor':'',
                        'baseboard_heating_type':baseboard_heating_type,
                        'baseboard_heating_availability_schedule_name':'',
                        'baseboard_heating_capacity':baseboard_heating_capacity,
                        }
                )
             
        #heating_setpoint_schedule_name
        heating_schedule=node.successor_node(name='has_heating_schedule')
        heating_setpoint_schedule_name=heating_schedule.id
        #add 'HVACTemplate:Thermostat' node
        self.output_epjson.add_node(
                labels='HVACTemplate:Thermostat',
                properties={
                        'id':template_thermostat_name,
                        'heating_setpoint_schedule_name':heating_setpoint_schedule_name,
                        'constant_heating_setpoint':'',
                        'cooling_setpoint_schedule_name':'',
                        'constant_cooling_setpoint':100
                        }
                )
        return
        
           
    def _map_schedule_node(self,node):
        "Adds a 'Schedule' node"
        name=node.id
        ys=node.year_schedule
        self._map_schedule_schedule_year(name,ys)
    
    
    def _map_schedule_schedule_year(self,name,ys):
        "adds the Schedule:Year object"
        d={}
        for i,ps in enumerate(ys.seq):
            name1=name+'_ws{}'.format(i+1)
            e={'schedule_week_name_{}'.format(i+1):name1,
               'start_month_{}'.format(i+1):ps.begin_date.month,
               'start_day_{}'.format(i+1):ps.begin_date.day,
               'end_month_{}'.format(i+1):ps.end_date.month,
               'end_day_{}'.format(i+1):ps.end_date.day}
            d.update(e)
            self._map_schedule_schedule_week_daily(name1,ps)
        n=self.output_epjson.add_node(
                labels='Schedule:Year',
                properties={
                        'id':name
                        }
                )
        n.properties.update(d)
        return
    
    
    def _map_schedule_schedule_week_daily(self,name,ps):
        "add the Schedule:Week:Daily object"
        for day_type,ds in ps.ws.ds_dict.items():
            name1=name+'_ds_'+day_type
            l=['']*12
            if day_type=='All':
                l[:]=[name1]*12
            else:
                raise Exception('Other day types need to be added')
            self._map_schedule_schedule_day_interval(name1,ds)
        n=self.output_epjson.add_node(
                labels='Schedule:Week:Daily',
                properties={
            'id':name,
            "monday_schedule_day_name":l[0],
            "tuesday_schedule_day_name":l[1] ,
            "wednesday_schedule_day_name":l[2] ,
            "thursday_schedule_day_name":l[3] ,
            "friday_schedule_day_name":l[4] ,
            "saturday_schedule_day_name": l[5],
            "sunday_schedule_day_name":l[6] ,
            "holiday_schedule_day_name": l[7],
            "customday1_schedule_day_name": l[8],
            "customday2_schedule_day_name": l[9],
            "summerdesignday_schedule_day_name": l[10],
            "winterdesignday_schedule_day_name": l[11]
                        }
                )
        return n
    
    
    def _map_schedule_schedule_day_interval(self,name,ds):
        "add the Schedule:Daily:Interval object"
        times=ds.timestamps
        values=ds.data
        l=[]
        for time,value in zip(times,values):
            if time.day==1:
                hour=time.hour
            if time.day==2 and time.hour==0:
                hour=24
            minute=time.minute
            d={'time':'until: {:02}:{:02}'.format(hour,minute),
               'value_until_time': value}
            l.append(d)
        n=self.output_epjson.add_node(
                labels='Schedule:Day:Interval',
                properties={
                        'id':name,
                        "interpolate_to_timestep": "Linear",
                        "data":l
                        }
                )
        return n
        
    
    def _map_space_node(self,node):
        """
        Adds a Zone 
        """
        name=node.id
        n=self.output_epjson.add_node(
                labels='Zone',
                properties={
                        'id':name
                        }
                )
        return n
        
        
    def _map_surface_node(self,node):
        """
        Adds a 'BuildingSurface:Detailed' node 
        """
        #set up
        surface_type_map={'SlabOnGrade':'Floor',
                          'Roof':'Roof',
                          'ExteriorWall':'Wall',
                          'Ceiling':'Ceiling',
                          'InteriorWall':'Wall'
                          }
        outside_boundary_condition_map={'Climate':'Outdoors',
                                        'Ground':'Ground',
                                        'Space':'Zone'
                                        }
        sun_exposure_map={'Outdoors':'SunExposed',
                          'Ground':'NoSun',
                          'Zone':'NoSun'}
        wind_exposure_map={'Outdoors':'WindExposed',
                           'Ground':'NoWind',
                           'Zone':'NoWind'}
        #name
        name=node.id
        #surface_type
        if node.Ground:
            surface_type='Floor'
        elif node.Climate and node.tilt==90:
            surface_type='Wall'
        elif node.Climate and node.tilt!=90:
            surface_type='Roof'
        else:
            surface_type='Ceiling'
        #construction_name
        construction_node=node.Construction[0]
        construction_name=construction_node.id
        #zone name
        inner_node=node.successor_node(name='inner_next_to')
        zone_name=inner_node.id
        #outside_boundary_condition
        outer_node=node.successor_node(name='outer_next_to')
        for k,v in outside_boundary_condition_map.items():
            if k in outer_node.labels:
                outside_boundary_condition=v
        #outside_boundary_condition_object
        if outside_boundary_condition=='Zone':
            outside_boundary_condition_object=outer_node.id
        else:
            outside_boundary_condition_object=''
        #sun_exposure
        sun_exposure=sun_exposure_map[outside_boundary_condition]
        #wind_exposure
        wind_exposure=wind_exposure_map[outside_boundary_condition]
        #vertices
        vertices=[]
        for x in node.outer_vertices:
            d={
                    "vertex_x_coordinate": x[0],
                    "vertex_y_coordinate": x[1],
                    "vertex_z_coordinate": x[2]
                }
            vertices.append(d)
        #number_of_vertices
        number_of_vertices=len(vertices)
        #add node
        n=self.output_epjson.add_node(
                labels='BuildingSurface:Detailed',
                properties={
                        'id':name,
                        'construction_name':construction_name,
                        'number_of_vertices':number_of_vertices,
                        'outside_boundary_condition':outside_boundary_condition,
                        'outside_boundary_condition_object': outside_boundary_condition_object,
                        'sun_exposure':sun_exposure,
                        'surface_type':surface_type,   
                        'vertices':vertices,
                        'wind_exposure':wind_exposure,
                        'zone_name':zone_name
                        }
              )
        return n
    
    
    def _map_window_material_gas_node(self,node):
        """
        Adds a 'WindowMaterial:Gas' node 
        """
        layer_element=node.predeccessor_node(label='LayerElement')
        layer=layer_element.predeccessor_node(label='Layer')
        name=layer.id
        n=self.output_epjson.add_node(
                labels='WindowMaterial:Gas',
                properties={
                        'id':name,
                        "gas_type": node.gas_type,
                        "thickness": layer.thickness
                        }
                )
            
        return n
    
    
    def _map_window_material_glazing_node(self,node):
        """
        Adds a 'WindowMaterial:Glazing' node 
        """
        layer_element=node.predeccessor_node(label='LayerElement')
        layer=layer_element.predeccessor_node(label='Layer')
        name=layer.id
        n=self.output_epjson.add_node(
                labels='WindowMaterial:Glazing',
                properties={
            'id':name,
            "back_side_infrared_hemispherical_emissivity": node.back_side_infrared_hemispherical_emissivit or 0.84,
            "back_side_solar_reflectance_at_normal_incidence": node.back_side_solar_reflectance_at_normal_incidence or 0.071,
            "back_side_visible_reflectance_at_normal_incidence": node.back_side_visible_reflectance_at_normal_incidence or 0.08,
            "conductivity": node.conductivity or 0.9,
            "dirt_correction_factor_for_solar_and_visible_transmittance": node.dirt_correction_factor_for_solar_and_visible_transmittance or 1.0,
            "front_side_infrared_hemispherical_emissivity": node.front_side_infrared_hemispherical_emissivity or 0.84,
            "front_side_solar_reflectance_at_normal_incidence": node.front_side_solar_reflectance_at_normal_incidence or 0.071,
            "front_side_visible_reflectance_at_normal_incidence": node.front_side_visible_reflectance_at_normal_incidence or 0.08,
            "infrared_transmittance_at_normal_incidence": node.infrared_transmittance_at_normal_incidence or 0,
            "optical_data_type": node.optical_data_type or "SpectralAverage",
            "poisson_s_ratio": node.poisson_s_ratio or 0.22,
            "solar_diffusing": node.solar_diffusing or "No",
            "solar_transmittance_at_normal_incidence": node.solar_transmittance_at_normal_incidence or 0.775,
            "thickness": layer.thickness,
            "visible_transmittance_at_normal_incidence": node.visible_transmittance_at_normal_incidence or 0.881,
            "young_s_modulus": node.young_s_modulus or 72000000000.0
                        }
                )
            
        return n
    
    
    def run(self):
        "Running the mapping, Bim object placed in self.output"
        
        #SET UP SELF.OUTPUT_IDF
        self.output_epjson=self.input_epjson.copy()
        
        #ADD NODES TO EpjsonGRAPH
        for n in self.input_bim.nodes:
            labels=n.labels
            if 'Building' in labels:
                self._map_building_node(n)
            if 'Space' in labels:
                self._map_space_node(n)
                self._map_infiltration_node(n)
            if 'Surface' in labels:
                self._map_surface_node(n)
            #continue
            
            if 'Opening' in labels:
                self._map_opening_node(n)
            if 'Construction' in labels:
                self._map_construction_node(n)
            if 'Material' in labels:
                self._map_material_node(n)
            if 'MaterialAirGap' in labels:
                self._map_material_air_gap_node(n)
            if 'WindowMaterialGlazing' in labels:
                self._map_window_material_glazing_node(n)
            if 'WindowMaterialGas' in labels:
                self._map_window_material_gas_node(n)
            if 'Schedule' in labels:
                self._map_schedule_node(n)
            if 'RoomHeater' in labels:
                self._map_room_heater_node(n)
            if 'People' in labels:
                self._map_people_node(n)
            if 'Light' in labels:
                self._map_light_node(n)
            if 'Appliance' in labels:
                self._map_appliance_node(n)
    
        

    
# tests

if __name__=='__main__':
    from pprint import pprint
    from bim_graph import BimGraph
    from energyplus_model import EnergyPlusModel
    
    print('TEST-BimToEpjsonMap.py')
    
    o=BimToEpjsonMap()
    g=BimGraph()
    g.read_pickle(r'../tests/bim_to_epjson_map/detached_house.pickle')
    o.input_bim=g
    o.run()
    g1=o.output_epjson
    pprint(g1.graph_dict())
    
    g1.write_epjson(r'../tests/bim_to_epjson_map/detached_house.epJSON')
    
    o=EnergyPlusModel()
    epexe_fp=r'C:\EnergyPlusV8-9-0\EnergyPlus'
    idf_fp=r'../tests/bim_to_epjson_map\detached_house.epJSON'
    epw_fp=r'C:\EnergyPlusV8-9-0\WeatherData\GBR_Birmingham.035340_IWEC.epw'
    out_fp='../tests/bim_to_epjson_map'
    o.run_energyplus(epexe_fp=epexe_fp,
                     idf_fp=idf_fp,
                     epw_fp=epw_fp,
                     out_fp=out_fp)
    print(o.output_err)
    
