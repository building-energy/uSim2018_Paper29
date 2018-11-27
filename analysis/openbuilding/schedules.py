# -*- coding: utf-8 -*-

import pandas as pd

try:
    from .timeseries import ContinuousTimeSeries
except ImportError:
    from timeseries import ContinuousTimeSeries

class DaySchedule(ContinuousTimeSeries):
    """ A class representing the schedule of a typical day
    """
    def __init__(self,series=None,seq=None):
        ContinuousTimeSeries.__init__(self,series)
        if series is None and seq:
            self.seq(seq)
    
    def json(self):
        l=[(str(index),value) for index,value in self.series.iteritems()]
        return l

    def __repr__(self):
        "Equivalent to the default repr method"
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
            )   
    
    
    def seq(self,seq):
        "Creates self.series based on seq i.e. '21' or '[0,1,1,0]'"
        if seq is None:
            return None
        if isinstance(seq,int) or isinstance(seq,float) or isinstance(seq,str):
            series=self._generate_constant_series(seq)
        if isinstance(seq,list):
            series=self._generate_equal_interval_series(seq)
        self.series=series
    
    
    def _generate_constant_series(self,seq):
        "Returns series based on seq if seq is a constant value"
        s=pd.Series(data=[seq,seq],
                        index=[pd.Timestamp('1/1/2001 00:00'),
                               pd.Timestamp('1/2/2001 00:00')]
                        )
        return s
        
    
    def _generate_equal_interval_series(self,seq):
        "Returns series based on seq if seq is a list of values"
        delta=pd.Timedelta('1 days')/len(seq)
        data=[]
        index=[]
        ts=pd.Timestamp('1/1/2001 00:00')
        for v in seq:
            data+=[v,v]
            index+=[ts,ts+delta]
            ts+=delta
        s=pd.Series(data=data,
                    index=index
                    )
        return s


class WeekSchedule():
    "A class representing a week schedule"
    
    def __init__(self,ds_dict=None):
        self.ds_dict=ds_dict
    
    def json(self):
        ""
        d={}
        for k,v in self.ds_dict.items():
            d[k]=v.json()
        return d
        
    
    
class PeriodSchedule():
    "This represents a schedule over a time period with a WeekSchedule"
    def __init__(self,
                 ws=None,
                 begin_date=pd.Timestamp(2001,1,1),
                 end_date=pd.Timestamp(2001,12,31)
                 ):
        self.ws=ws
        self.begin_date=begin_date
        self.end_date=end_date

    def json(self):
        return {'begin_date':str(self.begin_date),
                'end_date':str(self.end_date),
                'ws':self.ws.json()}


class YearSchedule():
    "This represent a schedule over a year"
    def __init__(self,seq=None):
        self.seq=[]
        if seq: self.seq=seq
        
    def json(self):
        l=[]
        for item in self.seq:
            if isinstance(item,PeriodSchedule):
                l.append(item.json())
        return l
