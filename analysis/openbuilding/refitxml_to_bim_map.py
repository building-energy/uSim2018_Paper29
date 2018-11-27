# -*- coding: utf-8 -*-

from .refitxml_graph import RefitxmlGraph
from .bim_graph import BimGraph
from openvariable import Variable, IntervalTimeSeries

    
class RefitxmlToBimMap():
    "A mapping object to transfer refitXML to Bim"
    
    def __init__(self,fp_xml=None):
        self.input_refitxml=None
        self.output_bim=None
        if fp_xml:
            refit=RefitxmlGraph()
            refit.read_xml(fp_xml)
            self.input_refitxml=refit
            self.run()


    def _bim_node(self,refitxml_node):
        "Returns the bim node with the same 'id' as the refitxml node"
        return self._bim_dict[refitxml_node.attributes.get('id')]
    
    
    def _refitxml_node(self,bim_node):
        "Returns the refitxml node with the same 'id' as the bim node"
        return self._refitxml_dict[bim_node.id]


    def _map_attributes(self,gbxml_node,bim_node):
        "Maps the attributes of the gbxml node"
        bim_node.properties.update(gbxml_node.attributes)


    def _map_meter(self,meter_out):
        "Maps a Meter node"
        meter_in=self._refitxml_node(meter_out)
        parent_in=meter_in.parent_node()
        parent_out=self._bim_node(parent_in)
        self.output_bim.add_edge(parent_out,meter_out,'contains')


    def _map_radiator(self,radiator_out):
        "Maps a Radiator node"
        radiator_in=self._refitxml_node(radiator_out)
        space_in_id=radiator_in.attributes['spaceIdRef']
        space_out=self._bim_dict[space_in_id]
        self.output_bim.add_edge(space_out,radiator_out,'contains')


    def _map_radiatorValve(self,radiatorValve_out):
        "Maps a RadiatorValve node"
        radiatorValve_in=self._refitxml_node(radiatorValve_out)
        parent_in=radiatorValve_in.parent_node()
        parent_out=self._bim_node(parent_in)
        self.output_bim.add_edge(parent_out,radiatorValve_out,'connects_to')


    def _map_roomThermostat(self,roomThermostat_out):
        "Maps a RoomThermostat node"
        roomThermostat_in=self._refitxml_node(roomThermostat_out)
        parent_in=roomThermostat_in.parent_node()
        parent_out=self._bim_node(parent_in)
        self.output_bim.add_edge(parent_out,roomThermostat_out,'contains')


    def _map_sensor(self,sensor_out):
        "Maps a Sensor node"
        sensor_in=self._refitxml_node(sensor_out)
        parent_in=sensor_in.parent_node()
        parent_out=self._bim_node(parent_in)
        self.output_bim.add_edge(parent_out,sensor_out,'has_sensor')


    def _map_space(self,space_out):
        "Maps a Space node"
        space_in=self._refitxml_node(space_out)
        parent_in=space_in.parent_node()
        parent_out=self._bim_node(parent_in)
        self.output_bim.add_edge(parent_out,space_out,'contains')


    def _map_timeseriesvariables(self,node_out):
        "Maps the TimeSeriesVariables of a node"
        node_in=self._refitxml_node(node_out)
        tsvs=node_in.TimeSeriesVariable
        for tsv in tsvs:
            var=Variable()
            var.id=tsv.attributes.get('id')
            var.units=tsv.attributes.get('units')
            if tsv.attributes.get('intervalType')=='FixedInterval':
                ts=IntervalTimeSeries()
                if tsv.attributes.get('intervalUnit')=='Minute':
                    ts.interval=tsv.attributes.get('intervalLength')+'T'
                if tsv.attributes.get('variableType')=='Air temperature':
                    key='air_temperature'
                    ts.method='mean'
                    var.ts=ts
                    var.name=key
                    node_out.properties[key]=var
                if tsv.attributes.get('variableType')=='Gas volume':
                    key='gas_volume'
                    ts.method='sum'
                    var.ts=ts
                    var.name=key
                    node_out.properties[key]=var
        

    def run(self):
        "Running the mapping, Bim object placed in self.output"
        
        o=self.output_bim=BimGraph()
        self._refitxml_dict={}
        self._bim_dict={}
        
        ground_out=o.add_node(labels='Ground')
        
        #Initial Node mappings
        for n in self.input_refitxml.nodes:
            id1=n.attributes.get('id')
            if id1: self._refitxml_dict[id1]=n
            label=n.labels[0]
            if label in ['Climate','Sensor',
                         'Building',
                         'Meter',
                         'Space','Plug','Radiator',
                         'RoomThermostat','RadiatorValve'
                         
                         ]:
                n1=o.add_node(labels=label)
                if id1: self._bim_dict[id1]=n1
                self._map_attributes(n,n1)
        
        #Edges and additional mapping
        for n in o.nodes:
            label=n.labels[0]
            if label in 'Sensor':
                self._map_timeseriesvariables(n)
                self._map_sensor(n)
            elif label in 'Space':
                self._map_timeseriesvariables(n)
                self._map_space(n)
            elif label in 'Meter':
                self._map_timeseriesvariables(n)
                self._map_meter(n)
            elif label in 'RoomThermostat':
                self._map_roomThermostat(n)
            elif label in 'Radiator':
                self._map_radiator(n)
            elif label in 'RadiatorValve':
                self._map_radiatorValve(n)
        

        return


# MAP NODES            
    
    def map_building_node(self,node):
        "Adds a building to the BimGraph"
        properties=node.attributes
        properties['Name']=properties['objectName']
        properties['CADModelAzimuth']=properties['orientation']
        n=self.output_bim.add_building_node()
        for k,v in properties.items(): n.properties[k]=v
        n.properties['_node']=node
        node.attributes['_node']=n
        return n
    
    def map_climate_node(self,node):
        "Adds a environment to the BimGraph"
        properties=node.attributes
        n=self.output_bim.add_environment_node()
        for k,v in properties.items(): n.properties[k]=v
        n.properties['_node']=node
        node.attributes['_node']=n
        return n
    
    
    def map_space_node(self,node):
        "Adds a Space to the BimGraph"
        properties=node.attributes
        properties['Name']=properties.get('objectName')
        properties['ConditionType']=properties.get('conditionType')
        properties['Area']=properties.get('area')
        properties['Volume']=properties.get('volume')
        n=self.output_bim.add_space_node()
        for k,v in properties.items(): n.properties[k]=v
        n.properties['_node']=node
        node.attributes['_node']=n
        return n
    
    
    def map_sensor_node(self,node):
        "Adds a Sensor to the BimGraph"
        properties=node.attributes
        for tsv in node.TimeSeriesVariables:
            properties[tsv.id]=tsv.attributes
        n=self.output_bim.add_sensor_node()
        for k,v in properties.items(): n.properties[k]=v
        n.properties['_node']=node
        node.attributes['_node']=n
        return n
    
    
#    def map_room_heater_node(self,node):
#        """Adds a room heater based on a gbXML Zone node
#    
#        """
#        #set up
#        id1=node.attributes.get('id',None)
#        label='{http://www.gbxml.org/schema}BaseboardHeatingCapacity'
#        baseboard_heating_capacity=node.child_node(label=label,
#                                                   return_type='text')
#        label='{http://www.gbxml.org/schema}BaseboardHeatingType'
#        baseboard_heating_type=node.child_node(label=label,
#                                               return_type='attributes',
#                                               key='unit')
#        #electric baseboard heater
#        if baseboard_heating_type=='Electric':
#            bb_id='ELECTRIC_BASEBOARD_HEATER_'+id1
#            n=self.output_bim.add_electric_room_heater_node(
#                    id1=bb_id,
#                    capacity=baseboard_heating_capacity
#                    )    
#            
#            n._node=node  # this relates the bim Heater node to the gbXML Zone node
#            node._node=n
#            return n
#        
#        
#    
#    
#    
#    def map_space_node(self,node):
#        "Maps a GbxmlGraph Space node to a BimGraph Space node"
#        #id1
#        id1=node.attributes.get('id',None)
#        #name
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        #area
#        area=node.child_node(label='{http://www.gbxml.org/schema}Area',
#                             return_type='text')
#        if area: area=float(area)
#        #volume
#        volume=node.child_node(label='{http://www.gbxml.org/schema}Volume',
#                               return_type='text')
#        if volume: volume=float(volume)
#        #infiltration_rate
#        label='{http://www.gbxml.org/schema}AirChangesPerHour'
#        infiltration_rate=node.child_node(label=label,
#                                          return_type='text')
#        if infiltration_rate: infiltration_rate=float(infiltration_rate)
#        #condition type
#        condition_type=node.attributes.get('conditionType')
#        #add node
#        n=self.output_bim.add_space_node(id1=id1,
#                                         name=name,
#                                         area=area,
#                                         volume=volume,
#                                         infiltration_rate=infiltration_rate,
#                                         condition_type=condition_type)
#        #connect 'in' and 'out' nodes
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_people_node(self,node):
#        "Maps a GbxmlGraph Space node to a BimGraph People node"
#        #id1
#        space_id=node.attributes.get('id',None)
#        id1=space_id+'_people'
#        #number_of_people
#        label='{http://www.gbxml.org/schema}PeopleNumber'
#        number_of_people=node.child_node(label=label,
#                                         return_type='text')
#        if number_of_people: number_of_people=float(number_of_people)
#        #person_heat_gain
#        label='{http://www.gbxml.org/schema}PeopleHeatGain'
#        person_heat_gain=node.child_node(label=label,
#                                         return_type='text')
#        if person_heat_gain: person_heat_gain=float(person_heat_gain)
#        #return if no people
#        if number_of_people is None: return
#        #add node
#        n=self.output_bim.add_people_node(id1=id1,
#                                          number_of_people=number_of_people,
#                                          person_heat_gain=person_heat_gain
#                                          )
#        #add an edge from the Space
#        space_out=node._node
#        self.output_bim.add_edge(space_out,n,'contains')
#        return n
#    
#    
#    def map_light_node(self,node):
#        "Maps a GbxmlGraph Space node to a BimGraph Light node"
#        #id1
#        space_id=node.attributes.get('id',None)
#        id1=space_id+'_light'
#        #heat_gain_per_area
#        label='{http://www.gbxml.org/schema}LightPowerPerArea'
#        heat_gain_per_area=node.child_node(label=label,
#                                          return_type='text')
#        if heat_gain_per_area: heat_gain_per_area=float(heat_gain_per_area)
#        #return if no heat_gain_per_area
#        if heat_gain_per_area is None: return
#        #add node
#        n=self.output_bim.add_light_node(id1=id1,
#                                         heat_gain_per_area=heat_gain_per_area
#                                         )
#        #add an edge from the Space
#        space_out=node._node
#        self.output_bim.add_edge(space_out,n,'contains')
#        return n
#    
#    
#    def map_appliance_node(self,node):
#        "Maps a GbxmlGraph Space node to a BimGraph Appliance node"
#        #id1
#        space_id=node.attributes.get('id',None)
#        id1=space_id+'_appliance'
#        #heat_gain_per_area
#        label='{http://www.gbxml.org/schema}EquipPowerPerArea'
#        heat_gain_per_area=node.child_node(label=label,
#                                          return_type='text')
#        if heat_gain_per_area: heat_gain_per_area=float(heat_gain_per_area)
#        #return if no heat_gain_per_area
#        if heat_gain_per_area is None: return
#        #add node
#        n=self.output_bim.add_appliance_node(id1=id1,
#                                             heat_gain_per_area=heat_gain_per_area
#                                             )
#        #add an edge from the Space
#        space_out=node._node
#        self.output_bim.add_edge(space_out,n,'contains')
#        return n
#    
#    
#    def map_surface_node(self,node):
#        "Maps a GbxmlGraph Surface node to a BimGraph Surface node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        surfaceType=node.attributes.get('surfaceType',None)
#        n1=node.child_node(label='{http://www.gbxml.org/schema}PlanarGeometry')
#        coordinates=self.input_gbxml2.coordinates(n1)
#        n=self.output_bim.add_surface_node(id1,
#                                           name,
#                                           surfaceType,
#                                           coordinates)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_opening_node(self,node):
#        "Maps a GbxmlGraph Opening node to a BimGraph Opening node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        openingType=node.attributes.get('openingType',None)
#        n1=node.child_node(label='{http://www.gbxml.org/schema}PlanarGeometry')
#        coordinates=self.input_gbxml2.coordinates(n1)
#        n=self.output_bim.add_opening_node(id1,
#                                           name,
#                                           openingType,
#                                           coordinates)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_construction_node(self,node):
#        "Maps a GbxmlGraph Construction node to a BimGraph Construction node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        uvalue=node.child_node(label='{http://www.gbxml.org/schema}U-value',
#                               return_type='text')
#        if uvalue: uvalue=float(uvalue)
#        n=self.output_bim.add_construction_node(id1,
#                                                name,
#                                                uvalue)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_material_node(self,node):
#        "Maps a GbxmlGraph Material node to a BimGraph OpaqueMaterial or OpaqueAirGap node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        #thickness
#        label='{http://www.gbxml.org/schema}Thickness'
#        t=node.child_node(label=label,return_type='text')
#        thickness=float(t) if t else t
#        #conductivity
#        label='{http://www.gbxml.org/schema}Conductivity'
#        t=node.child_node(label=label,return_type='text')
#        conductivity=float(t) if t else t
#        #density
#        label='{http://www.gbxml.org/schema}Density'
#        t=node.child_node(label=label,return_type='text')
#        density=float(t) if t else t
#        #specific_heat
#        label='{http://www.gbxml.org/schema}SpecificHeat'
#        t=node.child_node(label=label,return_type='text')
#        specific_heat=float(t) if t else t
#        #adds a OpaqueMaterial node or OpaqueAirgap node       
#        if conductivity:
#            n=self.output_bim.add_opaque_material_node(id1=id1,
#                                                       name=name,
#                                                       thickness=thickness,
#                                                       conductivity=conductivity,
#                                                       density=density,
#                                                       specific_heat=specific_heat)
#        else:
#            n=self.output_bim.add_opaque_airgap_node(id1=id1,
#                                                     name=name,
#                                                     thickness=thickness)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_window_type_node(self,node):
#        "Maps a GbxmlGraph WindowType node to a BimGraph Construction node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        uvalue=node.child_node(label='{http://www.gbxml.org/schema}U-value',
#                               return_type='text')
#        if uvalue: uvalue=float(uvalue)
#        n=self.output_bim.add_construction_node(id1,
#                                                name,
#                                                uvalue)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_glaze_node(self,node):
#        "Maps a GbxmlGraph Glaze node to a BimGraph GlazingMaterial node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        #thickness
#        label='{http://www.gbxml.org/schema}Thickness'
#        t=node.child_node(label=label,return_type='text')
#        thickness=float(t) if t else t
#        n=self.output_bim.add_glazing_material_node(id1,
#                                                    name,
#                                                    thickness)
#        n._node=node
#        node._node=n
#        return n
#    
#    
#    def map_gap_node(self,node):
#        "Maps a GbxmlGraph Gap node to a BimGraph GlazingGap node"
#        id1=node.attributes.get('id',None)
#        name=node.child_node(label='{http://www.gbxml.org/schema}Name',
#                             return_type='text')
#        gas_type=node.attributes.get('gas')
#        #thickness
#        label='{http://www.gbxml.org/schema}Thickness'
#        t=node.child_node(label=label,return_type='text')
#        thickness=float(t) if t else t
#        n=self.output_bim.add_glazing_gap_node(id1,
#                                               name,
#                                               thickness,
#                                               gas_type)
#        n._node=node
#        node._node=n
#        return n
#
#    def map_schedule_node(self,node,ws_dict):
#        "Maps a GbxmlGraph Schedule node to a BimGraph Schedule node"
#        seq=[]
#        for n in node.YearSchedules:
#            ps=self._map_schedule_YearSchedule(n,ws_dict)
#            seq.append(ps)
#        ys=YearSchedule(seq=seq) 
#        n=self.output_bim.add_schedule_node(node.id,
#                                            node.Name,
#                                            ys)
#        n._node=node
#        node._node=n
#        return n
#    
#    def _map_schedule_YearSchedule(self,element,ws_dict):
#        "Returns a PeriodSchedule object based on the YearSchedule element"
#        ps=PeriodSchedule(begin_date=pd.Timestamp(element.BeginDate.text),
#                          end_date=pd.Timestamp(element.EndDate.text),
#                          ws=ws_dict[element.WeekScheduleId.weekScheduleIdRef])
#        return ps
#    
    
#        



# MAP EDGES    
    
#    def map_space_edges(self,space_out):
#        "Maps the edges of a space node"
#        space_in=space_out._node
#        building_in=space_in.parent_node()
#        building_out=building_in._node
#        e=self.output_bim.add_edge(building_out,space_out,'contains')
#        return e
#    
#    
#    def map_surface_edges(self,
#                          surface_out,
#                          ground_out,
#                          climate_out
#                          ):
#        "Maps the edges of a Surface node"
#        
#        surface_in=surface_out._node
#        
#        surfaceType=surface_in.attributes.get('surfaceType')
#        if surfaceType in ['SlabOnGrade']:
#            adjacent_node=ground_out
#        elif surfaceType in ['ExteriorWall','Roof']:
#            adjacent_node=climate_out
#        
#        #inner next_to
#        n=self.input_gbxml2.surface_inner_object(surface_in)
#        if n:
#            space_out=n._node
#            self.output_bim.add_inner_next_to_edge(surface_out,space_out)
#        else:
#            self.output_bim.add_inner_next_to_edge(surface_out,adjacent_node)
#        
#        #outer next_to
#        n=self.input_gbxml2.surface_outer_object(surface_in)
#        if n:
#            space_out=n._node
#            self.output_bim.add_outer_next_to_edge(surface_out,space_out)
#        else:
#            self.output_bim.add_outer_next_to_edge(surface_out,adjacent_node)
#        
#        #construction 'has' edge
#        n=self.input_gbxml2.construction_node(surface_in)
#        if n:
#            self.output_bim.add_edge(surface_out,n._node,'has')
#        
#        #building edge
#        l=self.input_gbxml2.surface_building_nodes(surface_in)
#        for n in l:
#            self.output_bim.add_edge(n._node,surface_out,'contains')
#        
#        return
#    
#    
#    def map_opening_edges(self,
#                          opening_out,
#                          ground_out,
#                          climate_out
#                          ):
#        "Maps the edges of an Opening node"
#        
#        opening_in=opening_out._node
#        surface_in=opening_in.parent_node()
#        surface_out=surface_in._node
#        
#        #surface to opening 'contains'
#        self.output_bim.add_edge(surface_out,opening_out,'contains')
#        
#        #inner next_to
#        n=surface_out.inner_next_to
#        if n:
#            self.output_bim.add_inner_next_to_edge(opening_out,n)
#        
#        #outer next_to
#        n=surface_out.outer_next_to
#        if n:
#            self.output_bim.add_outer_next_to_edge(opening_out,n)
#        
#        #construction 'has' edge
#        n=self.input_gbxml2.construction_node(opening_in)
#        if n:
#            self.output_bim.add_edge(opening_out,n._node,'has')
#        n=self.input_gbxml2.window_type_node(opening_in)
#        if n:
#            self.output_bim.add_edge(opening_out,n._node,'has')
#            
#        #building edge
#        l=surface_out.is_contained_by
#        if l:
#            for n in l:
#                self.output_bim.add_edge(n._node,opening_out,'contains')
#        
#        return
#        
#    
#    def map_construction_edges(self,
#                               construction_out                         
#                               ):
#        "Maps the edges of a Construction node"
#        
#        construction_in=construction_out._node
#        
#        #add edges
#        if construction_in.tag()=='Construction':
#            l=self.input_gbxml2.construction_material_nodes(construction_in)
#            for i,n in enumerate(l):
#                self.output_bim.add_edge(construction_out,
#                                         n._node,
#                                         name='has',
#                                         properties={'index':i}
#                                         )
#        elif construction_in.tag()=='WindowType':
#            l=self.input_gbxml2.window_type_material_nodes(construction_in)
#            for i,n in enumerate(l):
#                self.output_bim.add_edge(construction_out,
#                                         n._node,
#                                         name='has',
#                                         properties={'index':i}
#                                         )
#        
#        return
#    
#    
#    def map_electric_room_heater_edges(self,
#                                       heater_out):
#        "Maps the edges of a ElectricRoomHeater node"
#        zone_in=heater_out._node
#        space_in=self.input_gbxml2.zone_space_node(zone_in)
#        space_out=space_in._node
#        heating_schedule_in=self.input_gbxml2.zone_heating_schedule_node(zone_in)
#        heating_schedule_out=heating_schedule_in._node
#        #add contains edge
#        self.output_bim.add_edge(space_out,
#                                 heater_out,
#                                 name='contains',
#                                 )
#        
#        #add has_heating_schedule edge
#        self.output_bim.add_edge(heater_out,
#                                 heating_schedule_out,
#                                 name='has',
#                                 properties={'type':'heating'}
#                                 )
#        return     
#
#
#    def map_people_edges(self,
#                         people_out):
#        "Maps the edges of a People node"
#        space_out=people_out.predeccessor_node(label='Space')
#        space_in=space_out._node
#        schedule_in=self.input_gbxml2.space_people_schedule_node(space_in)
#        schedule_out=schedule_in._node
#        #add 'has' edge to schedule
#        self.output_bim.add_edge(people_out,
#                                 schedule_out,
#                                 name='has',
#                                 )
#        return     
#
#
#    def map_light_edges(self,
#                        light_out):
#        "Maps the edges of a Light node"
#        space_out=light_out.predeccessor_node(label='Space')
#        space_in=space_out._node
#        schedule_in=self.input_gbxml2.space_light_schedule_node(space_in)
#        schedule_out=schedule_in._node
#        #add 'has' edge to schedule
#        self.output_bim.add_edge(light_out,
#                                 schedule_out,
#                                 name='has',
#                                 )
#        return     
#
#
#    def map_appliance_edges(self,
#                            appliance_out):
#        "Maps the edges of a Appliance node"
#        space_out=appliance_out.predeccessor_node(label='Space')
#        space_in=space_out._node
#        schedule_in=self.input_gbxml2.space_equipment_schedule_node(space_in)
#        schedule_out=schedule_in._node
#        #add 'has' edge to schedule
#        self.output_bim.add_edge(appliance_out,
#                                 schedule_out,
#                                 name='has',
#                                 )
#        return  
        
    

# tests

#if __name__=='__main__':
#    from pprint import pprint
#    from refitxml_graph import RefitxmlGraph
#    from refitxml_graph import RefitxmlNode  #  this seems to be needed to make the read_pickle work...?
#    
#    # get gbxml
#    refitxml=RefitxmlGraph()
#    refitxml.read_xml(r'../tests/refitxml_to_bim_map/REFIT_BUILDING_SURVEY_INTERNAL_170713.xml')
#    #refitxml.read_pickle(r'../tests/refitxml_to_bim_map/REFIT_BUILDING_SURVEY_INTERNAL_170713.pickle')
#    #pprint(refitxml.graph_dict()['nodes'][0])
#    
#    # map
#    o=RefitxmlToBimMap()
#    o.input_refitxml=refitxml
#    o.run()
#    bim=o.output_bim
#    #pprint(bim.graph_dict())
#    bim.write_json(r'../tests/refitxml_to_bim_map/bim.json')
#    bim.write_pickle(r'../tests/refitxml_to_bim_map/bim.pickle')