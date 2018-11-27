# -*- coding: utf-8 -*-

try:
    from .xml_graph import XmlGraph, XmlNode
except ImportError:
    from xml_graph import XmlGraph, XmlNode
    
class GbxmlGraph(XmlGraph):
    """A GbXML graph
    """
    
    
    @staticmethod
    def _node(graph,_id,node_tuple):
        """Returns a Node instance
        """
        return GbxmlNode(graph,_id,node_tuple)
    
    
    def add_node(self,
                 labels=None,
                 attributes=None,
                 text=None,
                 ns='{http://www.gbxml.org/schema}',
                 parent=None):
        "Adds a new node tuple to self._nodes"
        n=XmlGraph.add_node(self,
                            labels=labels,
                            attributes=attributes,
                            text=text,
                            ns=ns,
                            parent=parent)
        return n
    
    
        
    def rename_node_id(self,node,new_id):
        """
        Renames the nodes 'id' attribute and updates the spaceIdRef links
        """
        old_id=node.attributes['id']
        node.attributes['id']=new_id
        tag=node.labels[0]
        lower_tag=tag.lower()
        id_ref=lower_tag+'IdRef'
        for n in self.nodes:
            if id_ref in n.attributes:
                if n.attributes[id_ref]==old_id:
                    n.attributes[id_ref]=new_id
        return node
    
    
    def remove_node(self,node):
        """Deletes a node from the graph
        
        If the node has an 'id' attribute, then all idRefs attributes
            in the graph are also deleted
        
        """
        XmlGraph.remove_node(self,node)
        
        if 'id' in node.attributes:
            old_id=node.attributes['id']
            tag=node.labels[0]
            lower_tag=tag.lower()
            id_ref=lower_tag+'IdRef'
            for n in self.nodes:
                if id_ref in n.attributes:
                    if n.attributes[id_ref]==old_id:
                        del n.attributes[id_ref]
        return node
    

class GbxmlNode(XmlNode):
    "A gbXML node"
    
    
    def CAD_model_azimuth(self):
        "Returns the CADModelAzimuth for a node"
        campus=self.ancestor_node('Campus')
        return campus.Location[0].CADModelAzimuth[0].text
    
    
    def construction_layer_nodes(self):
        "Returns the layer nodes for a construction"
        label='LayerId'
        LayerId_nodes=self.child_nodes(label=label)
        layerIdRefs=[x.attributes.get('layerIdRef') for x in LayerId_nodes]
        l=[]
        for layerIdRef in layerIdRefs:
            for n in self._graph.nodes:
                if n.attributes.get('id')==layerIdRef:
                    l.append(n)
        return l
    
    
    def construction_node(self):
        "Returns the construction node"
        constructionIdRef=self.attributes.get('constructionIdRef')
        if constructionIdRef:
            for n in self._graph.nodes:
                if n.attributes.get('id')==constructionIdRef:
                    return n
        else:
            return None
        
        
    def construction_material_nodes(self):
        "Returns the material nodes for a construction"
        l=[]
        for n in self.construction_layer_nodes():
            for n1 in self.layer_material_nodes():
                l.append(n1)
        return l
    

    def coordinates(self):
        """Returns the coordinates of a Geometry node"""
        label='CartesianPoint'
        cartesianPoint_nodes=self.descendent_nodes(label=label)
        l=[(float(cp.child_nodes()[0].text),
            float(cp.child_nodes()[1].text),
            float(cp.child_nodes()[2].text)
            )
            for cp in cartesianPoint_nodes]
        return l
    
    
    def day_dayschedule_node(self):
        "Returns the DaySchedule node for a given Day node"
        dayScheduleIdRef=self.attributes.get('dayScheduleIdRef')
        for n in self._graph.nodes:
            if n.attributes.get('id')==dayScheduleIdRef:
                return n
        return None
        
    
    def layer_material_nodes(self):
        "Returns the material nodes for a layer"
        label='MaterialId'
        MaterialId_nodes=self.child_nodes(label=label)
        materialIdRefs=[x.attributes.get('materialIdRef') for x in MaterialId_nodes]
        l=[]
        for materialIdRef in materialIdRefs:
            for n in self._graph.nodes:
                if n.attributes.get('id')==materialIdRef:
                    l.append(n)
        return l
    
    
    def space_equipment_schedule_node(self):
        "Returns the Schedule node for the equipment schedule of a given Space node"
        equipmentScheduleIdRef=self.attributes.get('equipmentScheduleIdRef')
        if not equipmentScheduleIdRef: return None
        for n in self._graph.nodes:
            if n.attributes.get('id')==equipmentScheduleIdRef:
                return n
        return None
    
    
    def space_light_schedule_node(self):
        "Returns the Schedule node for the light schedule of a given Space node"
        lightScheduleIdRef=self.attributes.get('lightScheduleIdRef')
        if not lightScheduleIdRef: return None
        for n in self._graph.nodes:
            if n.attributes.get('id')==lightScheduleIdRef:
                return n
        return None
    
    
    def space_people_schedule_node(self):
        "Returns the Schedule node for the people schedule of a given Space node"
        peopleScheduleIdRef=self.attributes.get('peopleScheduleIdRef')
        if not peopleScheduleIdRef: return None
        for n in self._graph.nodes:
            if n.attributes.get('id')==peopleScheduleIdRef:
                return n
        return None
    
    
    def surface_building_nodes(self):
        "Returns the building nodes for a surface"
        spaces=[self.surface_inner_object(),
                self.surface_outer_object()
                ]
        l=[]
        for space in spaces:
            if not space: continue
            building=space.parent_node()
            l.append(building)
        return l
    
    
    def surface_inner_object(self):
        """Returns the inner node of a Surface node
        """
        label='AdjacentSpaceId'
        AdjacentSpaceId_nodes=self.child_nodes(label=label)
        if len(AdjacentSpaceId_nodes)==0:
            return None
        else:
            spaceIdRef=AdjacentSpaceId_nodes[0].attributes['spaceIdRef']
            for n in self._graph.nodes:
                if n.attributes.get('id')==spaceIdRef:
                    return n
                
                
    def surface_outer_object(self):
        """Returns the outer node of a Surface node
        """
        label='AdjacentSpaceId'
        AdjacentSpaceId_nodes=self.child_nodes(label=label)
        if len(AdjacentSpaceId_nodes)<2:
            return None
        else:
            spaceIdRef=AdjacentSpaceId_nodes[1].attributes['spaceIdRef']
            for n in self._graph.nodes:
                if n.attributes.get('id')==spaceIdRef:
                    return n
    
        
    def window_type_node(self):
        "Returns the WindowType node"
        windowTypeIdRef=self.attributes.get('windowTypeIdRef')
        if windowTypeIdRef:
            for n in self._graph.nodes:
                if n.attributes.get('id')==windowTypeIdRef:
                    return n
        else:
            return None
    
    
    def window_type_material_nodes(self):
        "Returns the material nodes for a WindowType"
        l=[]
        for n in self.child_nodes():
            if 'Glaze' in n.labels or 'Gap' in n.labels:
                l.append(n)
        return l
    
    
    def yearschedule_weekschedule_node(self):
        "Returns the WeekSchedule node for a given YearSchedule node"
        label='WeekScheduleId'
        WeekScheduleId_node=self.child_node(label=label)
        weekScheduleIdRef=\
            WeekScheduleId_node.attributes.get('weekScheduleIdRef')
        for n in self._graph.nodes:
            if n.attributes.get('id')==weekScheduleIdRef:
                return n
        return None
    
    
    def zone_space_node(self):
        "Returns the Space nodes for a given Zone node"
        Zone_id=self.attributes.get('id')
        l=[]
        for n in self._graph.nodes:
            label='Space'
            if n.attributes.get('zoneIdRef')==Zone_id and label in n.labels:
                l.append(n)
        return l
    
    
    def zone_heating_schedule_node(self):
        "Returns the Schedule node for the heating schedule of a given Zone node"
        heatSchedIdRef=self.attributes.get('heatSchedIdRef')
        if not heatSchedIdRef: return None
        for n in self._graph.nodes:
            if n.attributes.get('id')==heatSchedIdRef:
                return n
        return None
    
    
    
# tests    
    
from pprint import pprint
        
if __name__=='__main__':
    print('test-gbxmlgraph.py')
    
    print('test-instatiate graph')
    g=GbxmlGraph()
    pprint(g.graph_dict())
    
    print('test-readxml')
    #g.read_xml(r'../tests/xmlgraph/1_BasicBlock.xml')
    g.read_xml(r'../tests/xmlgraph/detached_house.gbxml')
    #label='{http://www.gbxml.org/schema}Construction'
    #l=[x for x in g.json() if label in x['labels']]
    #pprint(l)
    
    print(g.gbXML[0].Campus)
    
    h=g.copy()
    
    g.write_graphml(r'../tests/gbxml_graph/test.graphml')
    g.write_json(r'../tests/gbxml_graph/test.json')
    g.write_pickle(r'../tests/gbxml_graph/test.pickle')
    
    #    