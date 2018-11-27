# -*- coding: utf-8 -*-

import pandas as pd

try:
    from .graph import Graph
except ImportError:
    from graph import Graph
    
try:
    from .timeseries import IntervalTimeSeries
except ImportError:
    from timeseries import IntervalTimeSeries

class EsoGraph(Graph):
    """A class which can hold .eso data as a graph
    
    ONLY WORKS FOR SIMULATION VARIABLES AT PRESENT
        NOT DAILY, MONTHLY OR RUNPERIOD REPORT VARIABLES
    
    """
    
    def __init__(self,fp=None):
        Graph.__init__(self)
        if fp: self.read_eso(fp)

    def read_eso(self,fp):
        """Reads the eso file and places the information in a graph
        
        Arguments:
            - fp (str): the filepath of an eso file
        
        """
        #setup
        flag_data_dictionary=True
        self._node_dict={}
        # reads the lines in the eso file
        for line in open(fp,'r'):
            if line.startswith('End of Data Dictionary'):
                flag_data_dictionary=False
                continue
            if flag_data_dictionary:
                self._read_data_dictionary(line)
            else:
                self._read_data(line)
        #creates the time series and cleans up
        for n in self.nodes:
            # creates pd.Series from 'index' and 'data' properties
            index=n.properties['index']
            data=n.properties['data']
            s=pd.Series(index=index,data=data)
            # set timestamps to the start of the interval, not the end
            interval=n.properties['ts'].interval
            s.index=s.index-pd.Timedelta(interval)
            n.properties['ts'].series=s
            # cleanup by removing 'index' and 'data'
            del n.properties['index']
            del n.properties['data']
        return


    def _read_data_dictionary(self,line):
        """Reads a 'Data Dictionary' line
        
        If the line is a new variable, then a new Node is added to the graph
        
        Arguments:
            - line (str): a line from the eso file
            
        """
        def parse_data_dictionary_variable_line(line):
            "Returns the parameters for a variable line"
            #print(line)
            b=line.split(',')
            variable_eso_code=int(b[0])
            c=b[3].split('[')
            d=c[1].split(']')
            e=d[1].split('!')
            label=b[2].strip()
            variable_name=c[0].strip()
            units=d[0].strip()
            interval=e[1].strip()
            if interval=='Hourly': # converts interval to a pandas Timedelta string
                interval='1H'
            else:
                raise Exception('More code needed to parse interval')
            return variable_eso_code,label,variable_name,units,interval
        
        items=line.split(',')
        try:
            x=int(items[0])
        except ValueError:
            return
        if x>6:  # THIS SEEMED TO CHANGE IN V8.9 - IS THIS A CONSTANT?
            variable_eso_code,label,variable_name,units,interval=\
                parse_data_dictionary_variable_line(line)
            ts=IntervalTimeSeries(interval=interval)
            properties={'variable_name':variable_name,
                        'index':[],
                        'data':[],
                        'ts':ts,
                        'variable_eso_code':variable_eso_code,
                        'units':units}
            n=self.add_node(labels=label,
                            properties=properties)  
            self._node_dict[variable_eso_code]=n
        return
    
     
    def _read_data(self,line):
        """Read a 'Data' line and places the data into the Nodes
        
        Arguments:
            - line (str): a line from the eso file
        
        """
        def parse_timestamp_line(a):
            """Returns a datetime for the timestamp line
            
            Assumes the year is 2001.
            
            Arguments:
                - a (str): the simulation timestamp line, starts with '2' 
            
            """
            year=2001
            month=int(a[2].strip())
            day=int(a[3].strip())
            hour=int(a[5].strip())
            minute=int(float(a[6].strip()))
            if not hour==24:
                dt=pd.Timestamp(year,month,day,hour,minute)
            else:
                hour=0
                dt=pd.Timestamp(year,month,day,hour,minute)
                dt+=pd.Timedelta('1 day')
            return dt
        
        items=line.split(',')
        try:
            variable_eso_code=int(items[0])
        except ValueError:
            return    
        if variable_eso_code==2:
            dt=parse_timestamp_line(items)
            self._dt=dt
        elif variable_eso_code>6:
            value=float(items[1])
            n=self._node_dict[variable_eso_code]
            n.properties['index'].append(self._dt)
            n.properties['data'].append(value)
        return


# tests    
    
from pprint import pprint
        
if __name__=='__main__':
    print('TEST-EsoGraph')
    
    print('TEST-INSTANTIATE ESOGRAPH')
    g=EsoGraph()
    pprint(g.graph_dict())
    
    
    print('TEST-READ_ESO')
    g.read_eso(r'../tests/eso_graph/eplusout.eso')
    pprint(g.graph_dict())
    #print(g.idf_string())
    
    #for n in g.nodes:
    #    print(n.properties.keys())
    
    
    