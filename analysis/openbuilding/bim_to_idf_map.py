# -*- coding: utf-8 -*-

try:
    from .idf_graph import IdfGraph
except ImportError:
    from idf_graph import IdfGraph
    
class BimToIdfMap():
    "A mapping object to transfer BimGraph to IdfGraph"
    
    def __init__(self):
        
        input_idf=IdfGraph()
        input_idf.add_version()
        input_idf.add_timestep()
        input_idf.add_global_geometry_rules()
        input_idf.add_run_period()
        input_idf.add_site_ground_temperature_building_surface()
        input_idf.add_output_variable_dictionary()
        input_idf.add_output_variable(
                variable_name='Site Outdoor Air Drybulb Temperature')
        input_idf.add_output_variable(
                variable_name='Zone Mean Air Temperature')
        
        self.input_bim=None
        self.input_idf=input_idf
        self.output_idf=None
    
    
    def _map_appliance_node(self,node):
        """
        Adds a ElectricEquipment node to the IdfGraph
        """
        name=node.id
        space_node=node.predeccessor_node(label='Space')
        zone_name=space_node.id
        schedule=node.successor_node(name='has_fraction_schedule')
        schedule_name=schedule.id
        heat_gain_per_area=node.power_per_area
        #add Node
        n=self.output_idf.add_electric_equipment(
                   name=name,
                   zone_name=zone_name,
                   schedule_name=schedule_name,
                   design_level_calculation_method='Watts/Area',
                   design_level='',
                   watts_per_zone_floor_area=heat_gain_per_area
                   )
        return n
    
    
    def _map_building_node(self,node):
        """
        Adds a Building to the IdfGraph
        """
        name=node.id
        north_axis=node.orientation
        n=self.output_idf.add_building(name=name,
                                       north_axis=north_axis)
        return n
    
    
    def _map_construction_node(self,node):
        """
        Adds a Construction node to the IdfGraph
        """
        name=node.id
        layers=node.Layers()
        layer_ids=[n.id for n in layers]
        n=self.output_idf.add_construction(name=name,
                                           material_names=layer_ids)
        return n
    
    
    def _map_infiltration_node(self,node):
        """
        Adds a ZoneInfiltration:DesignFlowRate node to the IdfGraph
        """
        zone_name=node.id
        name=zone_name+'_infiltration'
        air_changes_per_hour=node.infiltration
        if not air_changes_per_hour: return
        #add constant schedule
        schedule_name=name+'_schedule'
        self.output_idf.add_schedule_constant(name=schedule_name,
                                              hourly_value=1
                                              )
        #add node
        n=self.output_idf.add_zone_infiltration_design_flow_rate(
                 name=name,
                 zone_name=zone_name,
                 schedule_name=schedule_name,
                 design_flow_rate_calculation_method='AirChanges/Hour',
                 design_flow_rate='',
                 flow_per_zone_floor_area='',
                 flow_per_exterior_surface_area='',
                 air_changes_per_hour=air_changes_per_hour
                 )
        return n
    
    
    def _map_layer_node(self,node):
        """
        Adds a materials to the IdfGraph
        
        """
        name=node.id
        layer_element=node.LayerElement[0]
        
        if layer_element.Material:
            material=layer_element.Material[0]
            n=self.output_idf.add_material(
                    name=name,
                    thickness=node.thickness,
                    roughness=material.roughness or "Smooth",
                    conductivity=material.conductivity,
                    density=material.density,
                    specific_heat=material.specific_heat,
                    thermal_absorptance=material.thermal_absorptance or 0.9,
                    solar_absorptance=material.solar_absorptance or 0.7,
                    visible_absorptance=material.visible_absorptance or 0.9
                    )
            return n
    
        if layer_element.MaterialAirGap:
            material=layer_element.MaterialAirGap[0]
            n=self.output_idf.add_material_air_gap(
                name=name,
                thermal_resistance=material.thermal_resistance or 0.18
            ) 
            return n
    
        if layer_element.WindowMaterialGlazing:
            material=layer_element.WindowMaterialGlazing[0]
            n=self.output_idf.add_window_material_glazing(
                name=name,
                thickness=node.thickness,
                solar_transmittance_at_normal_incidence=material.solar_transmittance_at_normal_incidence or 0.775,
                front_side_solar_reflectance_at_normal_incidence=material.front_side_solar_reflectance_at_normal_incidence or 0.071,
                back_side_solar_reflectance_at_normal_incidence=material.back_side_solar_reflectance_at_normal_incidence or 0.071,
                visible_transmittance_at_normal_incidence=material.visible_transmittance_at_normal_incidence or 0.881,
                front_side_visible_reflectance_at_normal_incidence=material.front_side_visible_reflectance_at_normal_incidence or 0.08,
                back_side_visible_reflectance_at_normal_incidence=material.back_side_visible_reflectance_at_normal_incidence or 0.08,
                infrared_transmittance_at_normal_incidence=material.infrared_transmittance_at_normal_incidence or 0,
                front_side_infrared_hemispherical_emissivity=material.front_side_infrared_hemispherical_emissivity or 0.84,
                back_side_infrared_hemispherical_emissivity=material.back_side_infrared_hemispherical_emissivity or 0.84,
                conductivity=material.conductivity or 0.9
            )
            
        if layer_element.WindowMaterialGas:
            material=layer_element.WindowMaterialGas[0]
            n=self.output_idf.add_window_material_gas(
                name=name,
                gas_type=material.gas_type,
                thickness=node.thickness
                )
            return n
        
        
    def _map_light_node(self,node):
        """
        Adds a Lights node to the IdfGraph
        """
        name=node.id
        space_node=node.predeccessor_node(label='Space')
        zone_name=space_node.id
        schedule=node.successor_node(name='has_fraction_schedule')
        schedule_name=schedule.id
        heat_gain_per_area=node.power_per_area
        #add Node
        n=self.output_idf.add_lights(
                   name=name,
                   zone_name=zone_name,
                   schedule_name=schedule_name,
                   design_level_calculation_method='Watts/Area',
                   lighting_level='',
                   watts_per_zone_floor_area=heat_gain_per_area
                   )
        return n
    

    def _map_opening_node(self,node):
        """
        Adds a 'FenestrationSurface:Detailed' node to IdfGraph
        """
        #set up
#        opening_type_map={'FixedWindow':'Window',
#                          'NonSlidingDoor':'Door',
#                          'Air':'Air'}
        #name
        name=node.id
        surface_type='Door'
        #construction_name
        construction_node=node.Construction[0]
        construction_name=construction_node.id
        #surface_type
        layers=construction_node.Layers()
        layer_elements=[n.LayerElement[0] for n in layers]
        materials=[n.successor_node(name='has') for n in layer_elements]
        material_labels=[n.labels[0] for n in materials]
        if 'WindowMaterialGlazing' in material_labels:
            surface_type='Window'
        else:
            surface_type='Door'
        
        #building_surface_name
        surface_node=node.predeccessor_node(label='Surface',
                                            name='contains')
        building_surface_name=surface_node.id
        #number_of_vertices
        vertices=node.outer_vertices
        number_of_vertices=len(vertices)
        #vertices
        l=[y for x in vertices for y in x]
        #add node
        n=self.output_idf.add_fenestration_surface_detailed(
               name=name,
               surface_type=surface_type,
               construction_name=construction_name,
               building_surface_name=building_surface_name,
               outside_boundary_condition_object='',
               view_factor_to_ground='autocalculate',
               shading_control_name='',
               frame_and_divider_name='',
               multiplier=1,
               number_of_vertices=number_of_vertices,
               vertices=l,
               )
        return n
    
    
    def _map_people_node(self,node):
        """
        Adds a People node to the IdfGraph
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
        self.output_idf.add_schedule_constant(
          name=activity_level_schedule_name,
          hourly_value=person_heat_gain
          )
        #add People Node
        n=self.output_idf.add_people(
           name=name,
           zone_name=zone_name,
           number_of_people_schedule_name=number_of_people_schedule_name,
           number_of_people_calculation_method='People',
           number_of_people=number_of_people,
           people_per_zone_floor_area='',
           zone_floor_area_per_person='',
           fraction_radiant=0.3,
           sensible_heat_fraction='autocalculate',
           activity_level_schedule_name=activity_level_schedule_name
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
        template_thermostat_name=name+'_thermostat'
        #baseboard_heating_capacity
        baseboard_heating_capacity=node.capacity
        #add 'HVACTemplate:Zone:BaseboardHeat' node
        self.output_idf.add_HVAC_template_zone_baseboard_heat(
              zone_name=zone_name,
              template_thermostat_name=template_thermostat_name,
              zone_heating_sizing_factor='',
              baseboard_heating_type='Electric',
              baseboard_heating_availability_schedule_name='',
              baseboard_heating_capacity=baseboard_heating_capacity,
              )
        
        #heating_setpoint_schedule_name
        heating_schedule=node.successor_node(name='has_heating_schedule')
        heating_setpoint_schedule_name=heating_schedule.id
        #add 'HVACTemplate:Thermostat' node
        self.output_idf.add_HVAC_template_thermostat(
             name=template_thermostat_name,
             heating_setpoint_schedule_name=heating_setpoint_schedule_name,
             constant_heating_setpoint='',
             cooling_setpoint_schedule_name='',
             constant_cooling_setpoint=100
             )

        return
    
    
    def _map_schedule_node(self,node):
        """
        Adds a 'Schedule' node to the IdfGraph
        """
        #set up
        ys=node.year_schedule
        name=node.id
        
        #add_schedule_year
        self._map_schedule_schedule_year(name,ys)
        
        return
    
    
    def _map_schedule_schedule_day_hourly(self,name,ds):
        "add the Schedule:Daily:Hourly object"
        times=ds.timestamps
        values=ds.data
        
        self.output_idf.add_schedule_day_interval(
                name=name,
                interpolate_to_timestep='Linear',
                times=times,
                values=values
                )
    
    
    def _map_schedule_schedule_week_daily(self,name,ps):
        "add the Schedule:Week:Daily object"
        for day_type,ds in ps.ws.ds_dict.items():
            name1=name+'_ds_'+day_type
            l=['']*12
            if day_type=='All':
                l[:]=[name1]*12
            else:
                raise Exception('Other day types need to be added')
            self._map_schedule_schedule_day_hourly(name1,ds)
        self.output_idf.add_schedule_week_daily(name,
                                                *l)
        
    
    def _map_schedule_schedule_year(self,name,ys):
        "adds the Schedule:Year object"
        l=[]
        for i,ps in enumerate(ys.seq):
            name1=name+'_ws'+str(i)
            d={'schedule_week_name':name1,
               'start_month':ps.begin_date.month,
               'start_day':ps.begin_date.day,
               'end_month':ps.end_date.month,
               'end_day':ps.end_date.day}
            l.append(d)
            self._map_schedule_schedule_week_daily(name1,ps)
        self.output_idf.add_schedule_year(name=name,
                                          weekSchedules=l)
    
    
    def _map_space_node(self,node):
        """
        Adds a Zone to the IdfGraph
        """
        name=node.id
        n=self.output_idf.add_zone(name=name)
        return n
    
    
    def _map_surface_node(self,node):
        """
        Adds a 'BuildingSurface:Detailed' node to the IdfGraph
        """
        #set up
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
        name=node.properties.get('id')
        #surface_type
        if node.Ground:
            surface_type='Floor'
        elif node.tilt==90:
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
        #view_factor_to_ground
        view_factor_to_ground=''
        #number_of_vertices
        vertices=node.outer_vertices
        number_of_vertices=len(vertices)
        #vertices
        l=[y for x in vertices for y in x]
        #add node
        n=self.output_idf.add_building_surface_detailed(
              name=name,
              surface_type=surface_type,
              construction_name=construction_name,
              zone_name=zone_name,
              outside_boundary_condition=outside_boundary_condition,
              outside_boundary_condition_object=outside_boundary_condition_object,
              sun_exposure=sun_exposure,
              wind_exposure=wind_exposure,
              view_factor_to_ground=view_factor_to_ground,
              number_of_vertices=number_of_vertices,
              vertices=l
              )
        return n
    
    
    def run(self):
        "Running the mapping, Bim object placed in self.output"
        
        #SET UP SELF.OUTPUT_IDF
        self.output_idf=self.input_idf.copy()
        
        #ADD NODES TO IDFGRAPH
        
        for n in self.input_bim.nodes:
            labels=n.labels
            if 'Building' in labels:
                self._map_building_node(n)
            if 'Space' in labels:
                self._map_space_node(n)
                self._map_infiltration_node(n)
            if 'Surface' in labels:
                self._map_surface_node(n)
            if 'Construction' in labels:
                self._map_construction_node(n)
            if 'Layer' in labels:
                self._map_layer_node(n)
            if 'Opening' in labels:
                self._map_opening_node(n)
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
    
    o=BimToIdfMap()
    g=BimGraph()
    g.read_pickle(r'../tests/bim_to_idf_map/detached_house.pickle')
    o.input_bim=g
    o.run()
    g1=o.output_idf
    pprint(g1.graph_dict())
    
    g1.write_idf(r'../tests/bim_to_idf_map/detached_house.idf')
    
    o=EnergyPlusModel()
    epexe_fp=r'C:\EnergyPlusV8-9-0\EnergyPlus'
    idf_fp=r'../tests/bim_to_idf_map\detached_house.idf'
    epw_fp=r'C:\EnergyPlusV8-9-0\WeatherData\GBR_Birmingham.035340_IWEC.epw'
    out_fp=r'../tests/bim_to_idf_map\sim'
    o.run_energyplus(epexe_fp=epexe_fp,
                     idf_fp=idf_fp,
                     epw_fp=epw_fp,
                     out_fp=out_fp)
    print(o.output_err)
    
#    print('TEST-BimToIdfMap.py')
#    
#    print('TEST-INSTANTIATE MAP')
#    o=BimToIdfMap()
#    print(o)
#    
#    print('TEST-INPUT GBXML')
#    g=BimGraph()
#    g.read_pickle(r'../tests/gbxml_to_bim_map/detached_house.pickle')
#    o.input_bim=g
#    #pprint(o.input_bim.json()[0])
#    
#    print('TEST_RUN')
#    o.run()
#    l=o.output_idf.json()
##    l=[x for x in o.output_bim.json() if 'OpaqueMaterial' in x['labels']]
#    #pprint(l)
#    
#    st=o.output_idf.idf_string()
#    print(st)
#    o.output_idf.write_idf(r'../tests/bim_to_idf_map/detached_house.idf')
#    
#    
#    
#    o.output_bim.write_pickle('bim.pickle')
#    o.output_bim.write_graphml('bim.graphml')