# -*- coding: utf-8 -*-

from lxml import etree

try:
    from .graph import Graph
except ImportError:
    from graph import Graph
    
try:
    from .graph import Node
except ImportError:
    from graph import Node


class XmlGraph(Graph):
    """An XML graph
    """
    
    
    @staticmethod
    def _filter__nodes_by_attribute(_nodes,key,value):
        "Returns the node _ids with an attribute 'key' = 'value'"
        l=[]
        for _id,node_tuple in _nodes.items():
            properties=node_tuple[1]
            attributes=properties['attributes']
            if key in attributes:
                if attributes[key]==value:
                    l.append(_id)
        return l
    
    
    @staticmethod
    def _node(self,_id,node_tuple):
        "Returns a Node instance"
        return XmlNode(self,_id,node_tuple)
    
    
    def add_child_edge(self,parent,child):
        """Adds a child relationship 
        """
        child_nodes=parent.child_nodes()
        if child_nodes==[]:
            self.add_edge(parent,
                          child,
                          name='first_child')
        else:
            self.add_edge(child_nodes[-1],
                          child,
                          name='next_sibling')
    
    
    def add_node(self,
                    labels=None,
                    attributes=None,
                    text=None,
                    ns=None,
                    parent=None):
        "Adds a new node tuple to self._nodes"
        if not attributes: attributes={}
        properties={'attributes':attributes,
                    'text':text,
                    'ns':ns}
        n=Graph.add_node(self,
                         labels=labels,
                         properties=properties)
        if parent: self.add_child_edge(parent,n)
        return n
    
    
    def filter_node_by_attribute(self,
                                key,
                                value):
        "Returns the first node filtered by attribute key:value pair"
        l=self.filter_nodes_by_attribute(key,
                                        value)
        if l:
            return l[0]
        else:
            return None
    
    
    def filter_nodes_by_attribute(self,
                                 key,
                                 value):
        "Returns the nodes filtered by attribute key:value pair"
        _ids=self._filter__nodes_by_attribute(self._nodes,key,value)
        return [self._node(self,_id,self._nodes[_id]) for _id in _ids]
    
    
    def read_xml(self,
                 filepath):
        """Reads an XMl file into the Xmlgraph format
        
        All xml elements elements are read as individual graph nodes
        Element attributes are placed as a dict in the node properties 
            dict item 'attributes'
        Element text is placed as a string in the node properties 
            dict item 'text'
        XML parent/child relationships are represented using 
            'first_child_node' and 'next_sibling_node' relationships
        
        Arguments:
            filepath (str): the filepath of the XML file
        
        """
        def add_element(self,element,parent):
            "Adds the xml element as a node in the graph"
            tag=element.tag
            ns=tag.split('}')[0]+'}'
            label=tag.split('}')[1]
            attributes=dict(element.attrib)  # {} if no attributes present
            if element.text is None:
                text=None
            else:
                text=element.text.strip()
            n=self.add_node(labels=label,
                               attributes=attributes,
                               text=text,
                               ns=ns,
                               parent=parent
                              )
            return n
        
        def add_child_elements(self,node,element):
            "Adds the child elements of element to the graph"
            for child in element:
                if isinstance(child,etree._Comment): continue
                node1=add_element(self,child,node)
                add_child_elements(self,node1,child)
        
        root=etree.parse(filepath).getroot() #use lxml etree to parse the xml file
        node=add_element(self,root,None)
        add_child_elements(self,node,root)


    def remove_node(self,node):
        """Deletes a node from the graph 
        """
        #first, delete all descendents
        descendents=node.descendent_nodes()
        for node1 in descendents:
            Graph.remove_node(self,node1)
            
        #second, add a new 'first_node' edge if needed
        first_sibling=node.all_siblings()[0]
        if node is first_sibling:
            parent_node=node.parent_node()
            if not parent_node is None:
                next_sibling=node.next_sibling()
                self.add_edge(parent_node,
                              next_sibling,
                              name='first_child')
                
        #third, add a new 'next sibling' edge if needed
        previous_sibling=node.previous_sibling()
        next_sibling=node.next_sibling()
        if not previous_sibling is None and not next_sibling is None:
            self.add_edge(previous_sibling,
                          next_sibling,
                          name='next_sibling')
            
        #finally, remove node
        Graph.remove_node(self,node)
    

    def root_node(self):
        "Returns the root node"
        for node in self.nodes:
            if len(node.in_edges)==0:
                return node


    def write_xml(self,
                  fp):
        "Writes the graph as an xml file"
        def xml_element(node):
            "Returns an xml element for node"
            label=node.ns+node.labels[0]
            e=etree.Element(label)
            #add attributes
            for k,v in node.attributes.items():
                e.set(k,v)
            #add text
            text=node.text
            if not text is None: e.text=text
            #add children
            for child_node in node.child_nodes():
                e1=xml_element(child_node)
                e.append(e1)
            return e
        
        root_node=self.root_node()
        root_element=xml_element(root_node)
        tree=etree.ElementTree(root_element)
        tree.write(fp,pretty_print=True,xml_declaration=True,encoding="utf-8")
        
        
        
class XmlNode(Node):
    """An xml node
    """
    
    def __getattr__(self,key):
        """Returns successor nodes or properties with label 'key'
        
        If value has no 's' at the end, then a single Node or None is returned
        If value has an 's' at the end, then a list of Nodes is returned
        
        The priority is to look in self.properties first        
        
        """
        #print('__getattr__',key)
        if key.startswith('__') and key.endswith('__'):
            return super(XmlNode, self).__getattr__(key)
        elif key in self.properties:
            return self.properties[key]
        else:
            return self.child_nodes(label=key)
    
    
    def _return_types(self,nodes,return_type,key):
        "Returns the nodes, attributes or text"
        if return_type=='node': 
            return nodes
        elif return_type=='attributes':
            l=[n.attributes for n in nodes]
            if key:
                return [x.get(key) for x in l]
            else:
                return l
        elif return_type=='text':
            return [n.text for n in nodes]
    
    
    def all_next_siblings(self,label=None):
        """
        Returns all next sibling nodes of node, in order first to last
        
        """
        l=[]
        node=self
        while True:
            next_sibling=node.next_sibling()
            if next_sibling is None: break
            l.append(next_sibling)
            node=next_sibling
        if label:
            l=[x for x in l if label in x.labels]
        return l
    
    
    def all_previous_siblings(self,label=None):
        """
        Returns all previous sibling nodes of node, 
            in order first (nearest to node) to last (furthest from node)
        
        """
        l=[]
        node=self
        while True:
            previous_sibling=node.previous_sibling()
            if previous_sibling is None: break
            l.append(previous_sibling)
            node=previous_sibling
        if label:
            l=[x for x in l if label in x.labels]
        return l


    def all_siblings(self,label=None):
        """
        Returns all sibling nodes of node, in order first to last
        
        """
        l=list(reversed(self.all_previous_siblings())) \
                    + [self] \
                    + self.all_next_siblings()
        if label:
            l=[x for x in l if label in x.labels]
        return l


    def ancestor_node(self,
                     label=None):
        """
        Returns first the ancestor of a node ,in no particular order
        
        """
        l=self.ancestor_nodes(label)
        if not l: 
            return None
        else:
            return l[0]              
    
    
    def ancestor_nodes(self,label=None):
        """
        Returns all ancestors of node, 
            in order first (nearest to node) to last (furthest from node)
        
        """
        l=[]
        node=self
        while True:
            parent_node=node.parent_node()
            if parent_node is None: break
            l.append(parent_node)
            node=parent_node
        if label:
            l=[x for x in l if label in x.labels]
        return l
    
    
    def child_node(self,
                   label=None,
                   return_type='node',
                   key=None):
        """
        Return the first child nodes of node
        
        """
        l=self.child_nodes(label,return_type,key)
        if not l: 
            return None
        else:
            return l[0]
    
    
    def child_nodes(self,
                    label=None,
                    return_type='node',
                    key=None):
        """
        Return all child nodes of node
        
        """
        first_child=self.first_child()
        if first_child is None: 
            return []
        else:
            l=first_child.all_siblings()
        if label:
            l=[x for x in l if label in x.labels]
        l=self._return_types(l,return_type,key)
        return l
    
    
    def descendents_nested(self):
        """
        Returns all descendents of node, in a nested dictionary fashion 
        
        """
        d={}
        child_nodes=self.child_nodes()
        for child_node in child_nodes:
            d[child_node]=child_node.descendents_nested()
        return d
    
    
    def descendent_node(self,
                         label=None,
                         return_type='node',
                         key=None):
        """
        Returns first descendents of node as a list, in no particular order
        
        """
        l=self.descendent_nodes(label,return_type,key)
        if not l: 
            return None
        else:
            return l[0]
        
    
    def descendent_nodes(self,
                         label=None,
                         return_type='node',
                         key=None):
        """
        Returns all descendents of node as a list, in no particular order
        
        """
        child_nodes=self.child_nodes()
        if child_nodes==[]: return []
        l=child_nodes
        for child_node in child_nodes:
            l=l+child_node.descendent_nodes()
        if label:
            l=[x for x in l if label in x.labels]
        l=self._return_types(l,return_type,key)
        return l
    
    
    def first_child(self):
        """Returns the first_child node
        """
        for edge in self.out_edges:
            if edge.name=='first_child':
                return edge.end_node
        return None
    
    
    def parent_node(self):
        """
        Returns the parent node 
        
        """
        first_sibling=self.all_siblings()[0]
        for edge in first_sibling.in_edges:
            if edge.name=='first_child':
                return edge.start_node
        return None
    
        
    def previous_sibling(self):
        """Returns the previous sibling 
        """
        for edge in self.in_edges:
            if edge.name=='next_sibling':
                return edge.start_node
        return None
    
    
    def next_sibling(self):
        """Returns the next_sibling node
        """
        for edge in self.out_edges:
            if edge.name=='next_sibling':
                return edge.end_node
        return None
    
    
#    def ns(self):
#        "Returns the namespace of the node label, including the '{}'s"
#        return self.labels[0][:-len(self.tag)] 
#    
#    
#    def tag(self):
#        "Returns the tag of the node label, i.e without the namespace"
#        return self.labels[0].split('}')[1]


# tests
        
from pprint import pprint
        
if __name__=='__main__':
    print('test-xmlgraph.py')
    
    g=XmlGraph()
    #n=g.add_node()
    #pprint(g.graph_dict())
    #print(dir(n))
    
    print('test-readxml')
    g.read_xml(r'../tests/xmlgraph/1_BasicBlock.xml')
    #pprint(g.graph_dict()['nodes'])
    
    h=g.copy()
    #print(h.graph_dict()['nodes'][464])

    root=g.root_node()
    print(root.labels)
    print(root._node_tuple)
    print(root.first_child().labels)
    
    
    
    g.write_graphml(r'../tests/xmlgraph/test.graphml')
    g.write_json(r'../tests/xmlgraph/test.json')
    g.write_pickle(r'../tests/xmlgraph/test.pickle')
    
    
    