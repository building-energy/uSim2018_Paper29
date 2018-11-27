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


class GbxmlToBimMap():
    "A mapping object to transfer gbXML to Bim"
    
    
    map_keys={
            'Construction':{
                    'U-value':'uvalue'
                    },
            'Location':{
                    'Latitude':'latitude',
                    'Longitude':'longitude'
                    },
            'Space':{
                    'AirChangesPerHour':'infiltration',
                    'Area':'area',
                    'Volume':'volume'
                    },
            'Material':{
                    'Conductivity':'conductivity',
                    'Density':'density',
                    'SpecificHeat':'specific_heat'
                    },
            'WindowType':{
                    'U-value':'uvalue'
                    },
            'Gap':{
                    'gas':'gas_type'
                    }
            }
        
    
    def __init__(self):
        self.input_gbxml=None
        self.output_bim=None
    
    
    def _bim_node(self,gbxml_node):
        "Returns the bim node with the same 'id' as the gbxml node"
        return self._bim_dict[gbxml_node.attributes.get('id')]
    
    
    def _gbxml_node(self,bim_node):
        "Returns the gbxml node with the same 'id' as the bim node"
        return self._gbxml_dict[bim_node.id]
    
    
    def _map_attributes(self,gbxml_node,bim_node):
        "Maps the attributes of the gbxml node"
        bim_node.properties.update(gbxml_node.attributes)
        

    def _map_building(self,building_out):
        "Maps a space node"
        building_in=self._gbxml_node(building_out)
        building_out.orientation=float(building_in.CAD_model_azimuth())
        building_out.origin_vertex=[0.0,0.0,0.0]
        self.output_bim.add_edge(self.output_bim.Location[0],
                                 building_out,
                                 'contains')
     
    
    def _map_child_nodes_attributes(self,gbxml_node,bim_node):
        "Maps child nodes with attributes only"
        d={}
        for cn in gbxml_node.child_nodes():
            if cn.attributes and not cn.text and not cn.child_nodes():
                tag=cn.labels[0]
                for k,v in cn.attributes.items():
                    key=tag+'_'+k
                    if key in d:
                        d[key].append(v)
                    else:
                        d[key]=[v]
        if d:
            bim_node.properties.update(d)
        
        
    def _map_child_nodes_text(self,gbxml_node,bim_node):
        "Maps child nodes with text"
        d={}
        for cn in gbxml_node.child_nodes():
            text=cn.text
            if text:
                key=cn.labels[0]#.replace('-','')
                if key in d:
                        if not isinstance(d[key],list):
                            d[key]=[d[key]]
                        d[key].append(text)
                else:
                    d[key]=text
        if d:
            bim_node.properties.update(d)


    def _map_construction(self,construction_out):
        "Maps a construction node"
        #print(construction_out._node_tuple)
        k=1
        layer_out1_previous=None
        for i in construction_out.LayerId_layerIdRef:
            layer_out=self._bim_dict[i]
            #print(layer_out._node_tuple)
            for j in layer_out.MaterialId_materialIdRef:
                material_out=self._bim_dict[j]
                #print(material_out._node_tuple)
                
                layer_out1=self.output_bim.add_node(
                    labels='Layer',
                    properties={'id':layer_out.id + '_' + material_out.id + '_' + str(k),
                                'thickness':material_out.Thickness}
                    )
                k+=1
                
                if not layer_out1_previous:
                    self.output_bim.add_edge(construction_out,
                                  layer_out1,
                                  'outer_layer')
                else:
                    self.output_bim.add_edge(layer_out1_previous,
                                  layer_out1,
                                  'next_layer')
                layer_out1_previous=layer_out1
                
                layer_element_out1=self.output_bim.add_node(
                    labels='LayerElement',
                    properties={'id':layer_out.id + '_' + material_out.id + '_' + 'element',
                                'proportion':1}
                    )
                
                self.output_bim.add_edge(layer_out1,
                                         layer_element_out1,
                                         'contains')
                self.output_bim.add_edge(layer_element_out1,
                                         material_out,
                                         'has')
                

    def _map_coordinates(self,gbxml_node,bim_node):
        try:
            c=gbxml_node.PlanarGeometry[0].coordinates()
            bim_node.outer_vertices=c
        except IndexError:
            pass
        
        
    def _map_gap(self,gap_out):
        "Maps a Glaze node"
        gap_out.labels.clear()
        gap_out.labels.append('WindowMaterialGas')
        
        
    def _map_glaze(self,glaze_out):
        "Maps a Glaze node"
        glaze_out.labels.clear()
        glaze_out.labels.append('WindowMaterialGlazing')
        
        
    def _map_keys(self,bim_node):
        "Changes the properties key names"
        label=bim_node.labels[0]
        properties=bim_node.properties
        try:
            for k,v in GbxmlToBimMap.map_keys[label].items():
                try:
                    properties[v]=properties.pop(k)
                except KeyError:
                    pass
        except KeyError:
            return
        
        
    def _map_opening(self,opening_out):
        "Maps the edges of a Surface node"
        opening_in=self._gbxml_node(opening_out)
        
        self._map_coordinates(opening_in,opening_out)
        
        surface_in=opening_in.parent_node()
        surface_out=self._bim_node(surface_in)
        self.output_bim.add_edge(surface_out,
                                 opening_out,
                                 'contains')
        
        
        #'has_construction' edge
        id1=opening_out.constructionIdRef or opening_out.windowTypeIdRef
        if id1:
            construction_out=self._bim_dict[id1]
            self.output_bim.add_edge(opening_out,
                                     construction_out,
                                     'has_construction')
    
    
    def _map_material(self,material_out):
        "Maps a material node"
        conductivity=material_out.conductivity
        if not conductivity:
            material_out.labels.clear()
            material_out.labels.append('MaterialAirGap')
    
    
    def _map_schedule(self,schedule_out):
        "Maps a Schedule node"
        schedule_in=self._gbxml_node(schedule_out)
        seq=[]
        for year_schedule_in in schedule_in.YearSchedule:
            year_schedule_out=self._bim_node(year_schedule_in)
            ps=self._map_schedule_YearSchedule(year_schedule_out)
            seq.append(ps)
        ys=YearSchedule(seq=seq) 
        schedule_out.year_schedule=ys
    
    
    def _map_schedule_DaySchedule(self,day_schedule_out):
        "Returns a dict of DaySchedule objects"
        sv=day_schedule_out.ScheduleValue
        if not isinstance(sv,list): sv=[sv]
        seq=[float(x) for x in sv]
        ds=DaySchedule(seq=seq)
        return ds
    
    
    def _map_schedule_WeekSchedule(self,week_schedule_out):
        "Returns a WeekSchedule object"
        d={}
        for i,dayScheduleIdRef in enumerate(week_schedule_out.Day_dayScheduleIdRef):
            dt=week_schedule_out.Day_dayType[i]
            day_schedule_out=self._bim_dict[dayScheduleIdRef]
            ds=self._map_schedule_DaySchedule(day_schedule_out)
            d[dt]=ds
        ws=WeekSchedule(ds_dict=d)
        return ws
    
    
    def _map_schedule_YearSchedule(self,year_schedule_out):
        "Returns a PeriodSchedule object based on the YearSchedule"
        begin_date=pd.Timestamp(year_schedule_out.BeginDate)
        end_date=pd.Timestamp(year_schedule_out.EndDate)
        weekScheduleIdRef=year_schedule_out.WeekScheduleId_weekScheduleIdRef[0]
        week_schedule_out=self._bim_dict[weekScheduleIdRef]
        ws=self._map_schedule_WeekSchedule(week_schedule_out)
        ps=PeriodSchedule(begin_date=begin_date,
                          end_date=end_date,
                          ws=ws)
        return ps
    
    
    def _map_space(self,space_out):
        "Maps a space node"
        space_in=self._gbxml_node(space_out)
        building_in=space_in.parent_node()
        building_out=self._bim_node(building_in)
        self.output_bim.add_edge(building_out,space_out,'contains')
        
        
    def _map_space_Appliance(self,space_out):
        "Maps the people"
        power_per_area=space_out.EquipPowerPerArea
        if power_per_area:
            name=space_out.id+'_appliance'
            equipmentScheduleIdRef=space_out.equipmentScheduleIdRef
            appliance_schedule_out=self._bim_dict[equipmentScheduleIdRef]
            appliance_out=self.output_bim.add_node(
                    labels='Appliance',
                    properties={'id':name,
                                'power_per_area':power_per_area}
                    )
            self.output_bim.add_edge(space_out,
                                     appliance_out,
                                     'has_people')
            self.output_bim.add_edge(appliance_out,
                                     appliance_schedule_out,
                                     'has_fraction_schedule')


    def _map_space_Light(self,space_out):
        "Maps the people"
        power_per_area=space_out.LightPowerPerArea
        if power_per_area:
            name=space_out.id+'_light'
            lightScheduleIdRef=space_out.lightScheduleIdRef
            light_schedule_out=self._bim_dict[lightScheduleIdRef]
            light_out=self.output_bim.add_node(
                    labels='Light',
                    properties={'id':name,
                                'power_per_area':power_per_area}
                    )
            self.output_bim.add_edge(space_out,
                                     light_out,
                                     'has_people')
            self.output_bim.add_edge(light_out,
                                     light_schedule_out,
                                     'has_fraction_schedule')

        
    def _map_space_People(self,space_out):
        "Maps the people"
        number_of_people=space_out.PeopleNumber
        if number_of_people:
            name=space_out.id+'_people'
            heat_gain_per_person=space_out.PeopleHeatGain
            peopleScheduleIdRef=space_out.peopleScheduleIdRef
            people_schedule_out=self._bim_dict[peopleScheduleIdRef]
            people_out=self.output_bim.add_node(
                    labels='People',
                    properties={
                            'id':name,
                            'number_of_people':number_of_people,
                            'heat_gain_per_person':heat_gain_per_person
                            }
                    )
            self.output_bim.add_edge(space_out,
                                     people_out,
                                     'has_people')
            self.output_bim.add_edge(people_out,
                                     people_schedule_out,
                                     'has_fraction_schedule')
            

    def _map_surface(self,surface_out,climate_out,ground_out):
        "Maps the edges of a Surface node"
        surface_in=self._gbxml_node(surface_out)
        
        self._map_coordinates(surface_in,surface_out)
        
        surface_out.tilt=surface_in.RectangularGeometry[0].Tilt[0].text
        surface_out.azimuth=surface_in.RectangularGeometry[0].Azimuth[0].text
        
        surfaceType=surface_in.attributes.get('surfaceType')
        if surfaceType in ['SlabOnGrade']:
            adjacent_node=ground_out
        elif surfaceType in ['ExteriorWall','Roof']:
            adjacent_node=climate_out
        
        #inner next_to
        n=surface_in.surface_inner_object()
        if n:
            space_out=self._bim_node(n)
            self.output_bim.add_edge(surface_out,
                                     space_out,
                                     'inner_next_to')
        else:
            self.output_bim.add_edge(surface_out,
                                     adjacent_node,
                                     'inner_next_to')
        
        #outer next_to
        n=surface_in.surface_outer_object()
        if n:
            space_out=self._bim_node(n)
            self.output_bim.add_edge(surface_out,
                                     space_out,
                                     'outer_next_to')
        else:
            self.output_bim.add_edge(surface_out,
                                     adjacent_node,
                                     'outer_next_to')
        
        #'has_construction' edge
        id1=surface_out.constructionIdRef or surface_out.windowTypeIdRef
        if id1:
            construction_out=self._bim_dict[id1]
            self.output_bim.add_edge(surface_out,
                                     construction_out,
                                     'has_construction')
        
        #building edge
        l=surface_in.surface_building_nodes()
        for n in l:
            building_out=self._bim_node(n)
            self.output_bim.add_edge(building_out,
                                     surface_out,
                                     'contains')
    
    
    def _map_window_type(self,window_type_out):
        "Maps a GbxmlGraph WindowType node to a BimGraph Construction node"
        window_type_out.labels.clear()
        window_type_out.labels.append('Construction')
        window_type_in=self._gbxml_node(window_type_out)
        materials_in=window_type_in.window_type_material_nodes()
        layer_out_previous=None
        for material_in in materials_in:
            material_id=material_in.attributes.get('id')
            material_out=self._bim_dict[material_id]
            layer_id=material_id+'_layer'
            layer_element_id=layer_id+'_element'
            thickness=material_out.Thickness
            
            layer_out=self.output_bim.add_node(
                labels='Layer',
                properties={'id':layer_id,
                            'thickness':thickness}
                )
            
            if not layer_out_previous:
                self.output_bim.add_edge(window_type_out,
                                         layer_out,
                                         'outer_layer')
            else:
                self.output_bim.add_edge(layer_out_previous,
                                         layer_out,
                                         'next_layer')
            layer_out_previous=layer_out
            
            layer_element_out=self.output_bim.add_node(
                labels='LayerElement',
                properties={'id':layer_element_id,
                            'proportion':1}
                )
            
            self.output_bim.add_edge(layer_out,
                                     layer_element_out,
                                     'contains')
            self.output_bim.add_edge(layer_element_out,
                                     material_out,
                                     'has')
        
    
    def _map_zone(self,zone_out):
        "Maps a zone node"
        zone_in=self._gbxml_node(zone_out)
        spaces_in=zone_in.zone_space_node()
        
        for space_in in spaces_in:
        
            space_out=self._bim_node(space_in)
            name=space_out.id+'_room_heater'
            capacity=float(zone_out.BaseboardHeatingCapacity)
            fuel_type=zone_out.BaseboardHeatingType_unit[0]
            
            room_heater_out=self.output_bim.add_node(
                    labels='RoomHeater',
                    properties={
                            'id':name,
                            'capacity':capacity,
                            'fuel_type':fuel_type,
                            }
                        )
        
            self.output_bim.add_edge(space_out,
                                     room_heater_out,
                                     'contains')
            
            heating_schedule_out=self._bim_dict[zone_out.heatSchedIdRef]
            
            self.output_bim.add_edge(room_heater_out,
                                     heating_schedule_out,
                                     'has_heating_schedule')
            
        

    def run(self):
        "Running the mapping, Bim object placed in self.output"
        
        o=self.output_bim=BimGraph()
        self._gbxml_dict={}
        self._bim_dict={}
        
        climate_out=o.add_node(labels='Climate')
        ground_out=o.add_node(labels='Ground')
        
        #Initial Node mappings
        for n in self.input_gbxml.nodes:
            id1=n.attributes.get('id')
            if id1: self._gbxml_dict[id1]=n
            label=n.labels[0]
            if label in ['Location','Building','Space',
                         'Surface','Opening',
                         'Construction','Layer','Material',
                         'WindowType','Glaze','Gap',
                         'Zone',
                         'Schedule','YearSchedule','WeekSchedule','DaySchedule'
                         ]:
                n1=o.add_node(labels=label)
                if id1: self._bim_dict[id1]=n1
                self._map_attributes(n,n1)
                self._map_child_nodes_text(n,n1)
                self._map_child_nodes_attributes(n,n1)
                self._map_keys(n1)
        
        #Edges and additional mapping
        for n in o.nodes:
            label=n.labels[0]
            if label in 'Building':
                self._map_building(n)
            elif label in 'Space':
                self._map_space(n)
                self._map_space_People(n)
                self._map_space_Light(n)
                self._map_space_Appliance(n)
            elif label in 'Zone':
                self._map_zone(n)
            elif label in 'Surface':
                self._map_surface(n,climate_out,ground_out)
            elif label in 'Opening':
                self._map_opening(n)
            elif label in 'Construction':
                self._map_construction(n)
            elif label in 'Material':
                self._map_material(n)
            elif label in 'WindowType':
                self._map_window_type(n)
            elif label in 'Glaze':
                self._map_glaze(n)
            elif label in 'Gap':
                self._map_gap(n)
            elif label in 'Schedule':
                self._map_schedule(n)
            for k,v in n.properties.items():
                try:
                    n.properties[k]=float(v)
                except ValueError:
                    pass
                except TypeError:
                    pass
    
        o.remove_orphan_nodes()


    
# tests

if __name__=='__main__':
    from pprint import pprint
    from gbxml_graph import GbxmlGraph
    
    # get gbxml
    gbxml=GbxmlGraph()
    gbxml.read_xml(r'../tests/gbxml_to_bim_map/detached_house.gbxml')
    
    # map
    o=GbxmlToBimMap()
    o.input_gbxml=gbxml
    o.run()
    bim=o.output_bim
    #pprint(bim.graph_dict()['edges'])
    pprint(bim.Surface[0]._node_tuple)
    
   
    #print(o.output_bim)
    bim.write_pickle(r'../tests/gbxml_to_bim_map/detached_house.pickle')
    bim.write_json(r'../tests/gbxml_to_bim_map/detached_house.json')
    bim.write_graphml(r'../tests/gbxml_to_bim_map/detached_house.graphml')
    
   