# -*- coding: utf-8 -*-

try:
    from .graph import Graph
except ImportError:
    from graph import Graph

class IdfGraph(Graph):
    """An Idf graph
    """
    
    def __init__(self):
        Graph.__init__(self)


# GRAPH METHODS


    def first_node(self):
        "Returns the first node in the graph"
        nodes=self.nodes
        if not nodes: return None
        for n in nodes:
            if not n.in_edges:
                return n


    def last_node(self):
        "Returns the last node in the graph"
        nodes=self.nodes
        if not nodes: return None
        for n in reversed(nodes):
            if not n.out_edges:
                return n


    def add_node(self,
                 labels=None,
                 properties=None):
        last_node=self.last_node()
        n=Graph.add_node(self,labels=labels,properties=properties)
        if last_node:
            self.add_edge(last_node,
                          n,
                          name='next')
        return n


    def remove_node(self,   # NEEDS TESTING
                    node):
        "Deletes the node and associated edges"
        if node.in_edges:
            previous_node=node.in_edges[0].start_node
        else:
            previous_node=None
        if node.out_edges:
            next_node=node.out_edges[0].end_node
        else:
            next_node=None
        #add new edge if needed
        if previous_node and next_node:
            self.add_edge(previous_node,
                          next_node,
                          name='next')
        #remove node
        Graph.remove_node(self,node)


# READ/WRITE METHODS


    def idf_string(self):
        "Returns an idf string based on the graph"
        st=''
        n=self.first_node()
        while True:
            st+=n.labels[0]
            st+=','
            for k,v in n.properties.items():
                st+=str(v)
                st+=','
            st=st[:-1]
            st+=';'
            st+='\n'
            if not n.out_edges: break
            n=n.out_edges[0].end_node
        return st
            
    
    def write_idf(self,fp):
        "Writes an idf file"
        with open(fp,'w') as f:
            st=self.idf_string()
            f.write(st)

    def _remove_comments_from_file_string(self,file_string):
        "Removes all text to the right of a '!' on each line"
        file_lines=file_string.split('\n')
        l=[]
        for line in file_lines:
            a=line.split('!')[0]
            if a: l.append(a)
        return '\n'.join(l)


    def _idf_object_lists_from_file_string(self,file_string):
        "Returns an idf file_string as a list of lists"
        a=self._remove_comments_from_file_string(file_string)
        b=a.split(';')[:-1]
        c=[x.strip() for x in b]
        l=[]
        for d in c:
            e=d.split(',')
            f=[x.strip() for x in e]
            l.append(f)
        return l


    def read_idf(self,fp):
        """Reads an idf file
        
        Note: this gives the properties keys as 'F1', 'F2' etc. rather
            than the 'A1' or 'N1' notation as seen in the idd file.
        """
        with open(fp,'r') as f:
            file_string=f.read()
        l=self._idf_object_lists_from_file_string(file_string)
        for x in l:
            labels=x[0]
            field_values=x[1:]
            properties={}
            for i,field_value in enumerate(field_values):
                key='F'+str(i+1)
                properties[key]=field_value
            self.add_node(labels=labels,
                          properties=properties)

# ADD OBJECT METHODS


    def add_building(self,
                     name=None,
                     north_axis=0,
                     terrain='Suburbs',
                     loads_convergence_tolerance_value=0.04,
                     temperature_convergence_tolerance_value=0.4,
                     solar_distribution='FullExterior',
                     maximum_number_of_warmup_days=25,
                     minimum_number_of_warmup_days=6
                     ):
        """
        Adds a 'Building' node
        """
        labels='Building'
        properties=\
             {'A1':name,
              'N1':north_axis,
              'A2':terrain,
              'N2':loads_convergence_tolerance_value,
              'N3':temperature_convergence_tolerance_value,
              'A3':solar_distribution,
              'N4':maximum_number_of_warmup_days,
              'N5':minimum_number_of_warmup_days,
             }
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_building_surface_detailed(self,
                 name=None,
                 surface_type=None,
                 construction_name=None,
                 zone_name=None,
                 outside_boundary_condition=None,
                 outside_boundary_condition_object=None,
                 sun_exposure='SunExposed',
                 wind_exposure='WindExposed',
                 view_factor_to_ground='autocalculate',
                 number_of_vertices='autocalculate',
                 vertices=[]
                 ):
        """
        Adds a 'BuildingSurface:Detailed' node
        """
        labels='BuildingSurface:Detailed'
        properties=\
             {'A1':name,
              'A2':surface_type,
              'A3':construction_name,
              'A4':zone_name,
              'A5':outside_boundary_condition,
              'A6':outside_boundary_condition_object,
              'A7':sun_exposure,
              'A8':wind_exposure,
              'N1':view_factor_to_ground,
              'N2':number_of_vertices,
             }
        i=3
        for vertex in vertices:
            properties['N'+str(i)]=vertex
            i+=1
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_construction(self,
                         name=None,
                         material_names=[],
                        ):
        """
        Adds a 'Construction' node
        """
        labels='Construction'
        properties={'A1':name}
        d={'A{}'.format(i+2):x for i,x in enumerate(material_names)}
        properties.update(d)
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_electric_equipment(self,
                   name=None,
                   zone_name=None,
                   schedule_name=None,
                   design_level_calculation_method='EquipmentLevel',
                   design_level='',
                   watts_per_zone_floor_area=''
                   ):
        """
        Adds a 'ElectricEquipment' node
        """
        labels='ElectricEquipment'
        properties=\
            {'A1':name,
             'A2':zone_name,
             'A3':schedule_name,
             'A4':design_level_calculation_method,
             'N1':design_level,
             'N2':watts_per_zone_floor_area
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_fenestration_surface_detailed(self,
                                        name=None,
                                        surface_type=None,
                                        construction_name=None,
                                        building_surface_name=None,        
                                        outside_boundary_condition_object=None,
                                        view_factor_to_ground='autocalculate',
                                        shading_control_name='',
                                        frame_and_divider_name='',
                                        multiplier=1,
                                        number_of_vertices='autocalculate',
                                        vertices=[]
                                       ):
        """
        Adds a 'FenestrationSurface:Detailed' node
        """
        labels='FenestrationSurface:Detailed'
        properties=\
             {'A1':name,
              'A2':surface_type,
              'A3':construction_name,
              'A4':building_surface_name,
              'A5':outside_boundary_condition_object,
              'N1':view_factor_to_ground,
              'A6':shading_control_name,
              'A7':frame_and_divider_name,
              'N2':multiplier,
              'N3':number_of_vertices
             }
        i=4
        for vertex in vertices:
            properties['N'+str(i)]=vertex
            i+=1
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_global_geometry_rules(self,
                                  starting_vertex_position='UpperLeftCorner',
                                  vertex_entry_direction='Counterclockwise',
                                  coordinate_system='Relative',
                                  daylighting_reference_point_coordinate_system='Relative',
                                  rectangular_surface_coordinate_system='Relative'
                                  ):
        """
        Adds the 'GlobalGeometryRules' node
        """
        labels='GlobalGeometryRules'
        properties=\
            {'A1':starting_vertex_position,
             'A2':vertex_entry_direction,
             'A3':coordinate_system,
             'A4':daylighting_reference_point_coordinate_system,
             'A5':rectangular_surface_coordinate_system
             }
        n=self.add_node(labels=labels,properties=properties)
        return n  
    
    
    def add_HVAC_template_thermostat(self,
                                     name=None,
                                     heating_setpoint_schedule_name='',
                                     constant_heating_setpoint='',
                                     cooling_setpoint_schedule_name='',
                                     constant_cooling_setpoint=''
                                     ):
        """
        Adds a 'HVACTemplate:Thermostat' node
        """
        labels='HVACTemplate:Thermostat'
        properties=\
            {'A1':name,
             'A2':heating_setpoint_schedule_name,
             'N1':constant_heating_setpoint,
             'A3':cooling_setpoint_schedule_name,
             'N2':constant_cooling_setpoint
             }
        n=self.add_node(labels=labels,properties=properties)
        return n   
    
    
    def add_HVAC_template_zone_baseboard_heat(self,
              zone_name=None,
              template_thermostat_name='',
              zone_heating_sizing_factor='',
              baseboard_heating_type='HotWater',
              baseboard_heating_availability_schedule_name='',
              baseboard_heating_capacity='autosize',
              ):
        """
        Adds a 'HVACTemplate:Zone:BaseboardHeat' node
        """
        labels='HVACTemplate:Zone:BaseboardHeat'
        properties=\
             {'A1':zone_name,
              'A2':template_thermostat_name,
              'N1':zone_heating_sizing_factor,
              'A3':baseboard_heating_type,
              'A4':baseboard_heating_availability_schedule_name,
              'N2':baseboard_heating_capacity
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_lights(self,
                   name=None,
                   zone_name=None,
                   schedule_name=None,
                   design_level_calculation_method='LightingLevel',
                   lighting_level='',
                   watts_per_zone_floor_area=''
                   ):
        """
        Adds a 'Lights' node
        """
        labels='Lights'
        properties=\
            {'A1':name,
             'A2':zone_name,
             'A3':schedule_name,
             'A4':design_level_calculation_method,
             'N1':lighting_level,
             'N2':watts_per_zone_floor_area
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_material(self,
                     name=None,
                     roughness=None,
                     thickness=None,
                     conductivity=None,
                     density=None,
                     specific_heat=None,
                     thermal_absorptance=None,
                     solar_absorptance=None,
                     visible_absorptance=None
                     ):
        """
        Adds a 'Material' node
        """
        labels='Material'
        properties=\
            {'A1':name,
             'A2':roughness,
             'N1':thickness,
             'N2':conductivity,
             'N3':density,
             'N4':specific_heat,
             'N5':thermal_absorptance,
             'N6':solar_absorptance,
             'N7':visible_absorptance
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_material_air_gap(self,
                             name=None,
                             thermal_resistance=None
                             ):
        """
        Adds a 'Material:AirGap' node
        """
        labels='Material:AirGap'
        properties=\
            {'0001_A1':name,
             '0002_N1':thermal_resistance
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_output_variable(self,
                            key_value='*',
                            variable_name=None,
                            reporting_frequency='Hourly'
                            ):
        """
        Adds a 'Output:Variable' node
        """
        labels='Output:Variable'
        properties=\
            {'A1':key_value,
             'A2':variable_name,
             'A3':reporting_frequency
             }
        n=self.add_node(labels=labels,properties=properties)
        return n   
    
    
    def add_output_variable_dictionary(self,
                                       key_field='IDF'
                                       ):
        """
        Adds a 'Output:VariableDictionary' node
        """
        labels='Output:VariableDictionary'
        properties=\
            {'A1':key_field}
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_people(self,
                   name=None,
                   zone_name=None,
                   number_of_people_schedule_name=None,
                   number_of_people_calculation_method='People',
                   number_of_people='',
                   people_per_zone_floor_area='',
                   zone_floor_area_per_person='',
                   fraction_radiant=0.3,
                   sensible_heat_fraction='autocalculate',
                   activity_level_schedule_name=None
                   ):
        """
        Adds a 'People' node
        """
        labels='People'
        properties=\
            {'A1':name,
             'A2':zone_name,
             'A3':number_of_people_schedule_name,
             'A4':number_of_people_calculation_method,
             'N1':number_of_people,
             'N2':people_per_zone_floor_area,
             'N3':zone_floor_area_per_person,
             'N4':fraction_radiant,
             'N5':sensible_heat_fraction,
             'A5':activity_level_schedule_name
             }
        n=self.add_node(labels=labels,properties=properties)
        return n

    
    def add_run_period(self,
                       name='RunPeriod1',
                       begin_month=1,
                       begin_day_of_month=1,
                       end_month=12,
                       end_day_of_month=31,
                       day_of_week_for_start_day='Sunday',
                       use_weather_file_holidays_and_special_days='No',
                       use_weather_file_daylight_saving_period='No',
                       apply_weekend_holiday_rule='No',
                       use_weather_file_rain_indicators='No',
                       use_weather_file_snow_indicators='No',
                       number_of_times_runperiod_to_be_repeated=1,
                       increment_day_of_week_on_repeat='Yes',
                       start_year=2001
                       ):
        """
        Adds the 'RunPeriod' node
        """
        labels='RunPeriod'
        properties=\
            {'A1':name,
             'N1':begin_month,
             'N2':begin_day_of_month,
             'N3':end_month,
             'N4':end_day_of_month,
             'A2':day_of_week_for_start_day,
             'A3':use_weather_file_holidays_and_special_days,
             'A4':use_weather_file_daylight_saving_period,
             'A5':apply_weekend_holiday_rule,
             'A6':use_weather_file_rain_indicators,
             'A7':use_weather_file_snow_indicators,
             'N5':number_of_times_runperiod_to_be_repeated,
             'A8':increment_day_of_week_on_repeat,
             'N6':start_year
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_schedule_constant(self,
                              name=None,
                              schedule_type_limits_name='',
                              hourly_value=0
                              ):
        """
        Adds a 'Schedule:Constant' node
        """
        labels='Schedule:Constant'
        properties=\
            {'A1':name,
             'A2':schedule_type_limits_name,
             'N1':hourly_value
             }
        n=self.add_node(labels=labels,properties=properties)
        return n  
    
    
    def add_schedule_day_hourly(self,
                                name=None,
                                schedule_type_limits_name='',
                                hourly_values=[0.0]*24
                                ):
        """
        Adds a 'Schedule:Day:Hourly' node
        
        """
        labels='Schedule:Day:Hourly'
        d={'A1':name,
           'A2':schedule_type_limits_name}
        for i,hourly_value in enumerate(hourly_values):
            d['N{}'.format(i+1)]=hourly_value
        properties=d
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_schedule_day_interval(self,
                                   name=None,
                                   schedule_type_limits_name='',
                                   interpolate_to_timestep='No',
                                   times=None,
                                   values=None
                                   ):
        """
        Adds a 'Schedule:Day:Interval' node
        
        """
        labels='Schedule:Day:Interval'
        d={'A1':name,
           'A2':schedule_type_limits_name,
           'A3':interpolate_to_timestep}
        for i,(time,value) in enumerate(zip(times,values)):
            if time.day==1:
                hour=time.hour
            if time.day==2 and time.hour==0:
                hour=24
            minute=time.minute
            d['A{}'.format(i+4)]='until: {:02}:{:02}'.format(hour,minute)
            d['N{}'.format(i+1)]=value
        properties=d
        n=self.add_node(labels=labels,properties=properties)
        return n  
    
    
    def add_schedule_week_daily(self,
                                name=None,
                                sunday_schedule_day_name=None,
                                monday_schedule_day_name=None,
                                tuesday_schedule_day_name=None,
                                wednesday_schedule_day_name=None,
                                thursday_schedule_day_name=None,
                                friday_schedule_day_name=None,
                                saturday_schedule_day_name=None,
                                holiday_schedule_day_name=None,
                                summerDesignDay_schedule_day_name=None,
                                winterDesignDay_schedule_day_name=None,
                                customDay1_schedule_day_name=None,
                                customDay2_schedule_day_name=None
                                ):
        """
        Adds a 'Schedule:Week:Daily' node
        
        """
        labels='Schedule:Week:Daily'
        properties=\
          {'A1':name,
           'A2':sunday_schedule_day_name,
           'A3':monday_schedule_day_name,
           'A4':tuesday_schedule_day_name,
           'A5':wednesday_schedule_day_name,
           'A6':thursday_schedule_day_name,
           'A7':friday_schedule_day_name,
           'A8':saturday_schedule_day_name,
           'A9':holiday_schedule_day_name,
           'A10':summerDesignDay_schedule_day_name,
           'A11':winterDesignDay_schedule_day_name,
           'A12':customDay1_schedule_day_name,
           'A13':customDay2_schedule_day_name
          }
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_schedule_year(self,
                          name=None,
                          schedule_type_limits_name='',
                          weekSchedules=[]
                          ):
        """
        Adds a 'Schedule:Year' node
        
        Arguments:
            weekSchedules (list) - a list of dicts {'schedule_week_name':str,
                                                    'start_month':int,
                                                    'start_day':int,
                                                    'end_month':int,
                                                    'end_day':int}
        
        """
        labels='Schedule:Year'
        d={'A1':name,
           'A2':schedule_type_limits_name}
        A=3
        N=1
        for weekSchedule in weekSchedules:
            d['A{}'.format(A)]=weekSchedule['schedule_week_name']
            A+=1
            d['N{}'.format(N)]=weekSchedule['start_month']
            N+=1
            d['N{}'.format(N)]=weekSchedule['start_day']
            N+=1
            d['N{}'.format(N)]=weekSchedule['end_month']
            N+=1
            d['N{}'.format(N)]=weekSchedule['end_day']
            N+=1
        properties=d
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_site_ground_temperature_building_surface(self,
            monthly_ground_temperatures=[18.0]*12  # a list with length 12
            ):
        """
        Adds the 'Site:GroundTemperature:BuildingSurface' node
        """
        labels='Site:GroundTemperature:BuildingSurface'
        properties=\
            {'N{}'.format(i+1):x 
             for i,x in enumerate(monthly_ground_temperatures)}
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_timestep(self,
                     number_per_hour=6):
        """
        Adds the 'Timestep' node
        """
        labels='Timestep'
        properties=\
            {'N1':number_per_hour}
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_version(self,
                    version_identifier='8.9'):
        """
        Adds the 'Version' node
        """
        labels='Version'
        properties=\
            {'A1':version_identifier}
        n=self.add_node(labels=labels,properties=properties)
        return n
        

    def add_zone(self,
                 name=None,
                 direction_of_relative_north=0,
                 x_origin=0,
                 y_origin=0,
                 z_origin=0,
                 type1=1,
                 multiplier=1,
                 ceiling_height='autocalculate',
                 volume='autocalculate',
                 floor_area='autocalculate',
                 zone_inside_convection_algorithm='',
                 zone_outside_convection_algorithm='',
                 part_of_total_floor_area='Yes'
                 ):
        """
        Adds a 'Zone' node
        """
        labels='Zone'
        properties=\
             {'A1':name,
              'N1':direction_of_relative_north,
              'N2':x_origin,
              'N3':y_origin,
              'N4':z_origin,
              'N5':type1,
              'N6':multiplier,
              'N7':ceiling_height,
              'N8':volume,
              'N9':floor_area,
              'A2':zone_inside_convection_algorithm,
              'A3':zone_outside_convection_algorithm,
              'A4':part_of_total_floor_area
             }
        n=self.add_node(labels=labels,properties=properties)
        return n
    
    
    def add_window_material_gas(self,
                                name=None,
                                gas_type=None,
                                thickness=None
                                ):
        """
        Adds a 'WindowMaterial:Gas' node
        """
        labels='WindowMaterial:Gas'
        properties=\
            {'A1':name,
             'A2':gas_type,
             'N1':thickness
             }
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_window_material_glazing(self,
          name=None,
          optical_data_type='SpectralAverage',
          window_glass_spectral_data_set_name='',
          thickness=None,
          solar_transmittance_at_normal_incidence=None,
          front_side_solar_reflectance_at_normal_incidence=None,
          back_side_solar_reflectance_at_normal_incidence=None,
          visible_transmittance_at_normal_incidence=None,
          front_side_visible_reflectance_at_normal_incidence=None,
          back_side_visible_reflectance_at_normal_incidence=None,
          infrared_transmittance_at_normal_incidence=0,
          front_side_infrared_hemispherical_emissivity=0.84,
          back_side_infrared_hemispherical_emissivity=0.84,
          conductivity=0.9,
          dirt_correction_factor_for_solar_and_visible_transmittance=1.0,
          solar_diffusing='No',
          Youngs_modulus='7.2e10',
          Poissons_ratio=0.22
          ):
        """
        Adds a 'WindowMaterial:Glazing' node
        """
        labels='WindowMaterial:Glazing'
        properties=\
         {'A1':name,
          'A2':optical_data_type,
          'A3':window_glass_spectral_data_set_name,
          'N1':thickness,
          'N2':solar_transmittance_at_normal_incidence,
          'N3':front_side_solar_reflectance_at_normal_incidence,
          'N4':back_side_solar_reflectance_at_normal_incidence,
          'N5':visible_transmittance_at_normal_incidence,
          'N6':front_side_visible_reflectance_at_normal_incidence,
          'N7':back_side_visible_reflectance_at_normal_incidence,
          'N8':infrared_transmittance_at_normal_incidence,
          'N9':front_side_infrared_hemispherical_emissivity,
          'N10':back_side_infrared_hemispherical_emissivity,
          'N11':conductivity,
          'N12':dirt_correction_factor_for_solar_and_visible_transmittance,
          'A4':solar_diffusing,
          'N13':Youngs_modulus,
          'N14':Poissons_ratio
         }
        n=self.add_node(labels=labels,properties=properties)
        return n


    def add_zone_infiltration_design_flow_rate(self,
                 name=None,
                 zone_name=None,
                 schedule_name=None,
                 design_flow_rate_calculation_method='AirChanges/Hour',
                 design_flow_rate='',
                 flow_per_zone_floor_area='',
                 flow_per_exterior_surface_area='',
                 air_changes_per_hour=''
                 ):
        """
        Adds a 'ZoneInfiltration:DesignFlowRate' node
        """
        labels='ZoneInfiltration:DesignFlowRate'
        properties=\
             {'A1':name,
              'A2':zone_name,
              'A3':schedule_name,
              'A4':design_flow_rate_calculation_method,
              'N1':design_flow_rate,
              'N2':flow_per_zone_floor_area,
              'N3':flow_per_exterior_surface_area,
              'N4':air_changes_per_hour
             }
        n=self.add_node(labels=labels,properties=properties)
        return n


    

    


    

    
    

                                                
    

    




        
    


                                       


                                              


    
    

    


    


    
    
    
    



    #ORIGINAL CODE - TO BE UPDATED
            
#    def idf_object_list(self,idf_object_string):
#        "Returns an idf_object_list based on an idf_object_string"
#        return idf_object_string.split(';')[0].split(',')
#
#    def idf_object_label(self,idf_object_list):
#        "Returns an idf_object_label based on an idf_object_list"
#        return idf_object_list[0]
#
#    def idf_object_properties(self,idf_object_list):
#        "Returns an idf_object_properties based on an idf_object_list"
#        return [str(x) for x in idf_object_list[1:]]
#
#    def idf_object_fields(self,idf_object_label):
#        "Returns an idf_object_fields based on an idf_object_label"
#        return list(self.idd[idf_object_label].keys())[1:]
#
#    def idf_object_dict(self,idf_object_list):
#        "Returns an idf_object_dict based on an idf_object_list"
#        label=self.idf_object_label(idf_object_list)
#        properties=self.idf_object_properties(idf_object_list)
#        fields=self.idf_object_fields(label)
#        return dict(zip(fields,properties))
#
#    def idf_dict(self,idf_object_lists):
#        "Returns an idf_dict based on an list of idf_object_lists"
#        d={}
#        for a in idf_object_lists:
#            obj_label=self.idf_object_label(a)
#            obj_dict=self.idf_object_dict(a)
#            self._append_to_dict(d,obj_label,obj_dict)
#        return d
#
#    def add_object_to_idf_dict(self,idf_object_list):
#        "Adds or appends an idf_object_list to the metaparameter idf_list"
#        obj_label=self.idf_object_label(idf_object_list)
#        obj_dict=self.idf_object_dict(idf_object_list)
#        if obj_label in self.metaparameters():
#            if not isinstance(self.metaparameters()[obj_label],list):
#                self.metaparameters()[obj_label]=[self.metaparameters()[obj_label]]
#            self.metaparameters()[obj_label].append(obj_dict)
#        else:
#            self.metaparameters()[obj_label]=obj_dict
#        return obj_label,obj_dict
#
#    
#    
#    def read_idd(self,file):
#        "Reads the idd file, using the bspy.Epidd object"
#        o=bspy.Epidd(file)
#        return o.idd_dict
#
#    def _append_to_dict(self,d,k,v):
#        """
#        Adds an item with key k and value v to dictionary d. Value v is added as a list i.e. [v] 
#        If there is already an item with key k, then v is appended to the existing value
#        """
#        if not k in d:
#            d[k]=[v]
#        else:
#            d[k].append(v)
#        return d    
#
#    def _parse_to_Bsgraph(self,idf_dict):
#        "Parses an idf_dict and places the data in the bsgraph objects and metaparameters"
#        def _add_idf_object(idf_object_label,idf_object_dict):
#            "add an idf_object as a bsgrpah object"
#            n=idf_object_dict['0001_A1']
#            self.add_objects(n)
#            self.add_labels(n,idf_object_label)
#            for k,v in idf_object_dict.items(): 
#                self.parameters(n)[k]=v
#            return n
#        #Climate
#        climate=self.add_objects('Climate1')
#        self.add_labels(climate,'Climate')
#        #Building
#        for d in idf_dict['Building']:
#            building=_add_idf_object('Building',d)
#        #Zones
#        for d in idf_dict['Zone']:
#            n=_add_idf_object('Zone',d)
#            self.add_contains(building,n)
#        #BuildingSurface:Detailed
#        for d in idf_dict['BuildingSurface:Detailed']:
#            n=_add_idf_object('BuildingSurface:Detailed',d)
#            #inner next_to
#            zone=d['0004_A4']
#            self.add_next_to(n,zone)
#            self.add_next_to(zone,n)
#            #outer next_to
#            outer=d['0005_A5']
#            if outer=='Outdoors':
#                self.add_next_to(n,climate)
#                self.add_next_to(climate,n)
#            self.add_contains(building,n)
#        #add remaining idf_dict objects
#        unique_labels=list(set([v for k,v in self.labels().items()]))
#        a=unique_labels
#        for k,v in idf_dict.items():
#            if not k in a:
#                self.metaparameters()[k]=v
#
#    def read(self,file):
#        "Reads an idf file"
#        with open(file,'r') as f:
#            file_string=f.read()
#        a=self._idf_object_lists_from_file_string(file_string)
#        b=self.idf_dict(a)    
#        self._parse_to_Bsgraph(b)

#    def idf_string(self):
#        "Returns an idf string based on the bsgraph objects and metaparameters"
#        st=''
#        #bsgraph objects
#        for n in self.objects():
#            #object strings
#            idf_object_label=self.labels(n)
#            if idf_object_label in ['Climate']: continue
#            idf_object_properties=list(self.parameters(n).values())
#            idf_object_properties=[str(x) for x in idf_object_properties]
#            st+=','.join([idf_object_label]+idf_object_properties)+';\n'
#        #bsgraph metaparameters
#        for k,v in self.metaparameters().items():
#            for v1 in v:
#                idf_object_label=k
#                idf_object_properties=list(v1.values())
#                idf_object_properties=[str(x) for x in idf_object_properties]
#                st+=','.join([idf_object_label]+idf_object_properties)+';\n' 
#        return st
#
#    def write(self,file):
#        "Writes an idf file"
#        with open(file,'w') as f:
#            st=self.idf_string()
#            f.write(st)

    
    
# tests    
    
from pprint import pprint
        
if __name__=='__main__':
    print('TEST-IdfGraph')
    
    print('TEST-INSTANTIATE GRAPH')
    g=IdfGraph()
    pprint(g.graph_dict())
    
    print('TEST-ADD OBJECTS')
    g.add_version()
    g.add_timestep()
    g.add_global_geometry_rules()
    g.add_run_period()
    g.add_site_ground_temperature_building_surface()
    pprint(g.graph_dict())
    print(g.idf_string())
    
    print('TEST-READ_IDF')
    g.clear()
    g.read_idf(r'../tests/idf_graph/detached_house.idf')
    pprint(g.graph_dict())
    print(g.idf_string())
#    pprint(g.json()[0:5])
#    
#    zones=[n for n in g.nodes if '{http://www.gbxml.org/schema}Zone' in n.labels]
#    g.remove_node(zones[0])
#    
#    g.write_xml('test.xml')