# -*- coding: utf-8 -*-

import pickle
import json
import copy
import sys


class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return obj.json()
        except AttributeError:
            pass
        # Let the base class default method raise the TypeError         
        return json.JSONEncoder.default(self, obj)
    

class Graph():
    """A Labelled Property Graph
    """
    
    def __init__(self):
        self._nodes={}  # a dict of {node._id:(labels,properties,_id_in_edges,_id_out_edges)}
        self._edges={}  # a dict of {edge._id:(start_node,end_node,name,properties)}
        self._id_count=0  # a counter to assign _ids to nodes
    
    
    def __getattr__(self,key):
        """Returns nodes with label 'key'
        
        If value has no 's' at the end, then a single Node or None is returned
        If value has an 's' at the end, then a list of Nodes is returned
        
        """
        if key.startswith('__') and key.endswith('__'):
            return super(Graph, self).__getattr__(key)
        else:
            return self.filter_nodes_by_label(label=key)
    
    
    @staticmethod
    def _filter__edges_by_name(_edges,name):
        "Returns the edge _ids with contain 'name'"
        l=[]
        for _id,edge_tuple in _edges.items():
            if name==edge_tuple[2]:
                l.append(_id)
        return l
    
    
    @staticmethod
    def _filter__edges_by_property(_edges,key,value):
        "Returns the edge _ids with a property 'key' = 'value'"
        l=[]
        for _id,edge_tuple in _edges.items():
            properties=edge_tuple[3]
            if key in properties:
                if properties[key]==value:
                    l.append(_id)
        return l
    
    
    @staticmethod
    def _filter__nodes_by_label(_nodes,label):
        "Returns the node _ids with contain 'label'"
        l=[]
        for _id,node_tuple in _nodes.items():
            labels=node_tuple[0]
            if label in labels:
                l.append(_id)
        return l
    
    
    @staticmethod
    def _filter__nodes_by_property(_nodes,key,value):
        "Returns the node _ids with a property 'key' = 'value'"
        l=[]
        for _id,node_tuple in _nodes.items():
            properties=node_tuple[1]
            if key in properties:
                if properties[key]==value:
                    l.append(_id)
        return l
    
    
    @staticmethod
    def _edge(graph,_id,edge_tuple):
        "Returns an Edge instance"
        return Edge(graph,_id,edge_tuple)
    

    def _fget_edges(self):
        "Returns a list of all edge instances in the graph"
        return [self._edge(self,_id,edge_tuple) for _id,edge_tuple in self._edges.items()]
    edges=property(_fget_edges)
    
    
    def _fget_nodes(self):
        "Returns a list of all node instances in the graph"
        return [self._node(self,_id,node_tuple) for _id,node_tuple in self._nodes.items()]
    nodes=property(_fget_nodes)
    
    
    @staticmethod
    def _node(graph,_id,node_tuple):
        "Returns a Node instance"
        return Node(graph,_id,node_tuple)
    
    
    def _Node(self,_id):
        "Returns a Node instance from this graph"
        graph=self
        node_tuple=self._nodes[_id]
        return self._node(graph,_id,node_tuple)
    
    

    def add_edge(self,
                 start_node,
                 end_node,
                 name=None,
                 properties=None):
        "Adds a new edge tuple to self._edges"
        _id=self._id_count
        _id_start_node=start_node._id
        _id_end_node=end_node._id
        if not name: name=''
        if not properties: properties={}
        edge_tuple=(_id_start_node,_id_end_node,name,properties)
        self._edges[_id]=edge_tuple
        self._id_count+=1
        self._nodes[_id_start_node][3].append(_id)
        self._nodes[_id_end_node][2].append(_id)
        return self._edge(self,_id,edge_tuple)

    
    def add_node(self,
                 labels=None,
                 properties=None):
        "Adds a new node tuple to self._nodes"
        _id=self._id_count
        if not labels: labels=[]
        if isinstance(labels,str): labels=[labels]
        if not properties: properties={}
        node_tuple=(labels,properties,[],[])
        self._nodes[_id]=node_tuple
        self._id_count+=1
        return self._node(self,_id,node_tuple)
    

    def clear(self):
        """Clears the graph, deletes all nodes"""
        self._nodes.clear()
        self._edges.clear()
        self.id_count=0 
    

    def copy(self):
        "returns a deep copy of the graph"
        return copy.deepcopy(self)
    
    
    def filter_edge_by_name(self,
                            name):
        "Returns the first edge filtered by name"
        l=self.filter_edges_by_name(name)
        if l:
            return l[0]
        else:
            return None
        
        
    def filter_edge_by_property(self,
                                key,
                                value):
        "Returns the first edge filtered by property"
        l=self.filter_edges_by_property(key,
                                        value)
        if l:
            return l[0]
        else:
            return None


    def filter_edges_by_name(self,
                             name):
        "Returns the edges filtered by name"
        _ids=self._filter__edges_by_name(self._edges,name)
        return [self._edge(self,_id,self._edges[_id]) for _id in _ids]  
    
    
    def filter_edges_by_property(self,
                                 key,
                                 value):
        "Returns the edges filtered by property key:value pair"
        _ids=self._filter__edges_by_property(self._edges,key,value)
        return [self._edge(self,_id,self._edges[_id]) for _id in _ids]
    

    def filter_node_by_label(self,label):
        "Returns the first node filtered by label"
        l=self.filter_nodes_by_label(label)
        if l:
            return l[0]
        else:
            return None
        
        
    def filter_node_by_property(self,
                                key,
                                value):
        "Returns the first node filtered by label"
        l=self.filter_nodes_by_property(key,
                                        value)
        if l:
            return l[0]
        else:
            return None


    def filter_nodes_by_label(self,label):
        "Returns the nodes filtered by label"
        _ids=self._filter__nodes_by_label(self._nodes,label)
        return [self._node(self,_id,self._nodes[_id]) for _id in _ids]


    def filter_nodes_by_property(self,
                                 key,
                                 value):
        "Returns the nodes filtered by property key:value pair"
        _ids=self._filter__nodes_by_property(self._nodes,key,value)
        return [self._node(self,_id,self._nodes[_id]) for _id in _ids]


    def graph_dict(self):
        "Returns the graph as a dictionary"
        d={}
        d['_id_count']=self._id_count
        d['nodes']=self._nodes
        d['edges']=self._edges
        return d


    def read_json(self,fp):
        pass
        #with open(fp,'r') as f:
        #    o=json.load(f)
        #CODE TO READ IN THE JSON OBJECT HERE...
        

    def read_pickle(self,fp):
        with open(fp,'rb') as f:
            g=pickle.load(f)
        self._id_count=g._id_count
        self._nodes=g._nodes
        self._edges=g._edges
        
    
    def remove_edge(self,
                    edge):
        _id=edge._id
        _id_start_node=edge._id_start_node
        _id_end_node=edge._id_end_node
        del self._edges[_id]
        self._nodes[_id_start_node][3].remove(_id)
        self._nodes[_id_end_node][2].remove(_id)
        return edge
    
    
    def remove_orphan_nodes(self):
        "Removes all nodes with no edges"
        l=[]
        for k,v in self._nodes.items():
            if not v[2] and not v[3]:
                l.append(k)
        for i in l:
            del self._nodes[i]
    
    
    def remove_node(self,
                    node):
        #remove edges which end at the node
        for e in node.in_edges:
            self.remove_edge(e)
        #remove edges that start at the node
        for e in node.out_edges:
            self.remove_edge(e)
        #remove node from self._nodes
        del self._nodes[node._id]
        return node
      
    
    def write_graphml(self,fp):
        "Writes a graphml file for visualising in Gephi"
        st='<graphml>'
        st+='<key attr.name="name" attr.type="string" for="edge" id="d1"/>'
        st+='<key attr.name="labels" attr.type="string" for="node" id="d0"/>'
        st+='<graph>'
        #add nodes
        for n in self.nodes:
            #add node
            a='<node id="{}"><data key="d0">{}</data></node>'
            st+=a.format(str(n._id),str(n.labels))
        #add edges
        for i,n in enumerate(self.nodes):
            for j,e in enumerate(n.out_edges):
                id1=str(i)+'-'+str(j)
                source=e.start_node._id
                target=e.end_node._id
                name=e.name
                b='<edge id="{}" source="{}" target="{}">' \
                  + '<data key="d1">{}</data></edge>'
                st+=b.format(id1,source,target,name)
        st+='</graph>'
        st+='</graphml>'
        with open(fp,'w') as f:
            f.write(st)
    
        
    def write_json(self,fp):
        with open(fp,'w') as f:
            json.dump(self.graph_dict(),
                      f,
                      sort_keys=True,
                      indent=4,
                      cls=MyJSONEncoder)
    

    def write_pickle(self,fp):
        #a=sys.getrecursionlimit()
        #sys.setrecursionlimit(100000)
        with open(fp,'wb') as f:
            pickle.dump(self,f)
        #sys.setrecursionlimit(a)
        

    
class Node():
    """A class representing a node in a Labelled Property Graph
    """
    
    def __init__(self,
                 graph,
                 _id,
                 node_tuple):
        self._graph=graph
        self._id=_id
        self._node_tuple=node_tuple
    
    
    def __getattr__(self,key):
        """Returns successor nodes or properties with label 'key'
        
        If value has no 's' at the end, then a single Node or None is returned
        If value has an 's' at the end, then a list of Nodes is returned
        
        The priority is to look in self.properties first        
        
        """
        if key.startswith('__') and key.endswith('__'):
            return super(Node, self).__getattr__(key)
        elif key in self.properties:
            return self.properties[key]
        else:
            return self.successor_nodes(label=key)
    
    
    def __setattr__(self,attr,value):
        """Sets an attribute
        
        if 'attr' is one of the Node attributes, 
            i.e. 'labels','properties','in_edges','out_edges'
            then it sets this attribute to 'value'
        
        otherwise the attr is added to the properties dict.
        
        """
        if attr in ['_graph','_id','_node_tuple']:
            self.__dict__[attr]=value
        else:
            self.properties[attr] = value
    
    
    def _fget__id_in_edges(self):
        return self._node_tuple[2]
    _id_in_edges=property(_fget__id_in_edges)
    
    
    def _fget__id_out_edges(self):
        return self._node_tuple[3]
    _id_out_edges=property(_fget__id_out_edges)
    
    
    def _fget_in_edges(self):
        return [self._graph._edge(self._graph,_id_in_edge,self._graph._edges[_id_in_edge])
                for _id_in_edge in self._id_in_edges]
    in_edges=property(_fget_in_edges)
    
    
    def _fget_labels(self):
        return self._node_tuple[0]
    labels=property(_fget_labels)
    
    
    def _fget_out_edges(self):
        return [self._graph._edge(self._graph,_id_out_edge,self._graph._edges[_id_out_edge]) 
                for _id_out_edge in self._id_out_edges]
    out_edges=property(_fget_out_edges)
    
    
    def _fget_properties(self):
        return self._node_tuple[1]
    properties=property(_fget_properties)
    
    
    def predeccessor_node(self,
                          label=None,
                          name=None):
        "Returns the first predeccessor node"
        l=self.predeccessor_nodes(label=label,
                                  name=name)
        if not l:
            return None
        else:
            return l[0]


    def predeccessor_nodes(self,
                           label=None,
                           name=None):
        "Returns the successor nodes"
        graph=self._graph
        #EDGES
        _id_edges=self._id_in_edges
        if not name is None:
            _edges={_id_edge:graph._edges[_id_edge] 
                    for _id_edge in _id_edges}
            _id_edges=Graph._filter__edges_by_name(_edges,
                                                  name)
        #NODES
        _id_nodes=[graph._edges[_id_edge][0] for _id_edge in _id_edges]
        if not label is None:
            _nodes={_id_node:graph._nodes[_id_node]
                    for _id_node in _id_nodes}
            _id_nodes=Graph._filter__nodes_by_label(_nodes,
                                                   label)
        nodes=[graph._node(graph,_id,graph._nodes[_id]) for _id in _id_nodes]
        return nodes


    def successor_node(self,
                       label=None,
                       name=None):
        "Returns the first successor node"
        l=self.successor_nodes(label=label,
                               name=name)
        if not l:
            return None
        else:
            return l[0]
        
    
    def successor_nodes(self,
                        label=None,
                        name=None):
        "Returns the successor nodes"
        graph=self._graph
        #EDGES
        _id_edges=self._id_out_edges
        if not name is None:
            _edges={_id_edge:graph._edges[_id_edge] 
                    for _id_edge in _id_edges}
            _id_edges=Graph._filter__edges_by_name(_edges,
                                                  name)
        #NODES
        _id_nodes=[graph._edges[_id_edge][1] for _id_edge in _id_edges]
        if not label is None:
            _nodes={_id_node:graph._nodes[_id_node]
                    for _id_node in _id_nodes}
            _id_nodes=Graph._filter__nodes_by_label(_nodes,
                                                   label)
        nodes=[graph._node(graph,_id,graph._nodes[_id]) for _id in _id_nodes]
        return nodes
    
    
class Edge():
    """A class representing an edge in a Labelled Property Graph
    
    This is a directed edge with a start and end node
    
    """
    
    def __init__(self,
                 graph,
                 _id,
                 edge_tuple):
        self._graph=graph
        self._id=_id
        self._edge_tuple=edge_tuple
            
    
    def __getattr__(self,key):
        """   
        
        """
        if key.startswith('__') and key.endswith('__'):
            return super(Edge, self).__getattr__(key)
        elif key in self.properties:
            return self.properties[key]
    
    
    def _fget__id_end_node(self):
        return self._edge_tuple[1]
    _id_end_node=property(_fget__id_end_node)
    
    
    def _fget__id_start_node(self):
        return self._edge_tuple[0]
    _id_start_node=property(_fget__id_start_node)
    
    
    def _fget_end_node(self):
        return self._graph._node(self._graph,
                                 self._id_end_node,
                                 self._graph._nodes[self._id_end_node])
    end_node=property(_fget_end_node)
    
    
    def _fget_name(self):
        return self._edge_tuple[2]
    name=property(_fget_name)
    
    
    def _fget_properties(self):
        return self._edge_tuple[3]
    properties=property(_fget_properties)
    
    
    def _fget_start_node(self):
        return self._graph._node(self._graph,
                                 self._id_start_node,
                                 self._graph._nodes[self._id_start_node])
    start_node=property(_fget_start_node)
    
    
    
# tests

from pprint import pprint
        
if __name__=='__main__':
    print('test-graph.py')
    
    print('test-instatiate graph')
    g=Graph()
    pprint(g.graph_dict())
    
    print('test-add first node')
    n=g.add_node(labels='Building',properties={'built_form':'detached'})
    pprint(g.graph_dict())
    print(n.built_form)
   
    print('test-add second node')
    n1=g.add_node(labels='Space')
    pprint(g.graph_dict())
    
    print('test-add edge')
    e=g.add_edge(g.nodes[0],g.nodes[1],'contains',{'index':1})
    pprint(g.graph_dict())
    
#    print('test-remove edge')
#    g.remove_edge(e)
#    pprint(g.graph_dict())
    
    print('test-remove second node')
    g.remove_node(g.nodes[1])
    pprint(g.graph_dict())
    
    print('test-add second node and edge')
    g.add_node(labels='Space')
    g.add_edge(g.nodes[0],g.nodes[1],'contains',{'index':1})
    pprint(g.graph_dict())
    
    print('test-remove first node')
    g.remove_node(g.nodes[0])
    pprint(g.graph_dict())
    
    print('test-copy graph')
    g.clear()
    n=g.add_node(labels='Building',properties={'built_form':'detached'})
    n1=g.add_node(labels='Space')
    e=g.add_edge(g.nodes[0],g.nodes[1],'contains',{'index':1})
    h=g.copy()
    pprint(h.graph_dict())
    
    print(g)
    print(g.filter_node_by_label('Building').labels)
    print(g.filter_node_by_property('built_form','detached').labels)
    print(g.filter_edge_by_name('contains').name)
    print(g.filter_edge_by_property('index',1).name)
    
    print(g.Building[0].successor_node().labels)
    print(g.Space[0].predeccessor_node().labels)
    
    #g.Building.properties['age']=1970
    g.Building[0].age=1970
    print(g._nodes)
    
    print(g.Building[0].out_edges[0]._id)
    
    
    g.write_graphml(r'../tests/graph/test.graphml')
    g.write_json(r'../tests/graph/test.json')
    g.write_pickle(r'../tests/graph/test.pickle')
    
    g.read_pickle(r'../tests/graph/test.pickle')
        
    #g.read_json(r'../tests/graph/test.json')

    
    