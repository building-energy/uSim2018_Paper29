# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class TimeSeries():
    """A class that holds time series data
    
    Attributes:
        - series (pd.Series) - a pandas Series with a Datetime index.
            The index must be in time order.
    
    """
    def __init__(self,series=None):
        if not series is None:
            self.series=series
        else:
            self.series=pd.Series()
    
    
    def _fget_timestamps(self):
        "Returns a list of the series timestamps"
        return list(self.series.index)
    timestamps=property(_fget_timestamps)


    def _fget_data(self):
        "Returns a list of the series data"
        return list(self.series.values)
    data=property(_fget_data)
    
    
    def date_vs_TOD(self):
        "Returns a DataFrame of self.series with index=times and columns=dates"
        s=self.series
        dates=s.index.date
        times=s.index.time
        s1=pd.Series(index=[dates,times],data=s.values)
        df=s1.unstack(level=0)
        return df
    
    
    def lookup(self,ts):
        """Returns the data value as time ts
        
        If there is no timestamp ts in self.series, then returns None
        
        If there are two timestamps with value ts, then the value of the
            lower one in the series is returned.
        
        Arguments:
            - ts (pd.Timestamp): 
        
        """
        try:
            v=self.series[ts]  # single value or new pd.Series
            if isinstance(v,pd.Series):  # if there is more than one timestamp with value ts
                v1=v[-1]  # returns the value of the last timestamp
                if not np.isnan(v1):
                    return v1
                else:
                    return None
            else:
                return v
        except KeyError:
            return None
    
    
    def nearest_timestamps(self,ts):
        """Returns the two nearest timestamps and their values
        
        Returns a tuple of length 4.
        
        First value is the timestamp which is nearest to and <= than ts,
            otherwise None
            
        Second value is the data value at this timestamp
        
        Third value is the next timestamp after the first value,
            otherwise None
            
        Fourth value is the data value at this timestamp
            
        """
        series=self.series
        index=series.index
        if len(index)==0:
            return None, None, None, None
        a=sum(index<=ts)
        # set lower
        if a==0:
            lower_ts=None
            lower_v=None
        else:
            lower_ts=index[a-1]
            lower_v=series[a-1]
            if np.isnan(lower_v): lower_v=None
        # set upper
        if a==len(index):
            upper_ts=None
            upper_v=None
        else:
            upper_ts=index[a]
            upper_v=series[a]
            if np.isnan(upper_v): upper_v=None
        # return tuple
        return lower_ts,lower_v,upper_ts,upper_v
    
    
    def plot(self):
        "a simple plot of the data"
        self.series.plot(style='o')
        
        
    def plot_colormap(self,ax):
        "plots a colormap of self.series"
        ax.set_xlabel('Date')
        ax.set_ylabel('Time')
        df=self.date_vs_TOD()
        x=df.columns
        y=df.index
        cmap = plt.get_cmap('plasma')
        im = ax.pcolormesh(x,y,df,cmap=cmap)
        ax.set_yticks(np.arange(0,3600*24,3600*3))
        return im
        
    
    def sample(self):
        """
        Look through all index and data values
        If any values have a 'sample' attribute then replace with value.sample()
        """
        i_l=[]
        v_l=[]
        for i,v in self.series.iteritems():
            if hasattr(i,'sample'):
                i_l.append(i.sample())
            else:
                i_l.append(i)
            if hasattr(v,'sample'):
                v_l.append(v.sample())
            else:
                v_l.append(v)
        s=pd.Series(data=v_l, index=i_l)
        return TimeSeries(series=s)
    

class DiscreteTimeSeries(TimeSeries):
    """A discrete time series data object
    """
    def __init__(self,series=None):
        TimeSeries.__init__(self,series)


    def __repr__(self):
        st='start_date={}'.format(self.timestamps[0])
        st+=',len={}'.format(len(self.series))
        return 'DiscreteTimeSeries({})'.format(st)


    def sample(self):
        dts=DiscreteTimeSeries()
        dts.series=TimeSeries.sample(self).series
        return dts



class IntervalTimeSeries(TimeSeries):
    """A fixed interval time series class
    
    The DatetimeIndex in self.series is the start of the intervals
    
    Attributes:
        
        - method (str): the aggregation method for the interval, 
            either 'mean' or 'sum'
    """
    def __init__(self,series=None,interval=None,method=None):
        TimeSeries.__init__(self,series)
        self.interval=interval
        self.method=method
    
    
    def __repr__(self):
        st='start_date="{}"'.format(self.timestamps[0] if self.timestamps else None)
        st+=', interval="{}"'.format(self.interval)
        st+=', method="{}"'.format(self.method)
        st+=', len={}'.format(len(self.series))
        return 'IntervalTimeSeries({})'.format(st)


    def lookup(self,ts):
        """Returns the data value at time ts.
        
        This will return the data value of an interval if:
            start_of_interval <= ts < end_of_interval
            
         Arguments:
            - ts (pd.Timestamp): 
            
        """
        v=TimeSeries.lookup(self,ts)
        if v:
            return v
        else:
            lower_ts,lower_v=self.nearest_timestamps(ts)[0:2]
            if lower_ts is None: return None
            upper_ts=lower_ts+self.interval
            if ts>=lower_ts and ts<upper_ts:
                return lower_v
            else:
                return None
            
            
    def json(self):
        "Returns a value for JSON serialization"
        d={
            'class':'IntervalTimeSeries',
            'interval':self.interval,
            'method':self.method
            }
        return d
        
    
    def plot(self,ax,name,units):
        ax.set_xlabel('Date')
        ax.set_ylabel('{} {} {} ({})'.format(self.interval,
                      self.method,
                      name,
                      units))
        x=self.series.index
        y=self.series.values
        ax.plot(x,y,linewidth=0.5)
        
        
    def hist(self,ax,bins=10,name=None,units=None):
        
        ax.set_xlabel(
            '{} bins ({}) (n={})'.format(
                name,
                units,
                bins)
            )
        ax.set_ylabel('Probability density')
        
        y=self.series.values
        ax.hist(y,bins=bins,density=True)
        
        
    def chist(self,ax,bins=10,name=None,units=None):
        
        ax.set_xlabel(
            '{} bins ({}) (n={})'.format(
                name,
                units,
                bins)
            )
        ax.set_ylabel('Cumulative probability density')
        
        y=self.series.values
        ax.hist(y,
                bins=bins,
                density=True,
                cumulative=True,
                histtype='step'
                )
    
        
class ContinuousTimeSeries(DiscreteTimeSeries):
    """A continuous interval time series class
    
    The values between data points are considered to be on a straight 
        line between the two nearest data points
        
    The DatetimeIndex in self.series can should be in time order, 
        but it can hold a repeat of the same timestamp to represent
        a step change.    
        
    If there are two data points at the same timestamp, then the later
        values in the series is chosen.
    
    """
    def __init__(self,series=None):
        TimeSeries.__init__(self,series)

    
    def __repr__(self):
        st='start_date={}'.format(self.timestamps[0])
        st+=',len={}'.format(len(self.series))
        return 'ContinuousTimeSeries({})'.format(st)
    
    
    def lookup(self,ts):
        """Returns the data value at time ts.
        
         Arguments:
            - ts (pd.Timestamp): 
            
        """
        v=TimeSeries.lookup(self,ts)
        if v:
            return v
        else:
            lower_ts,lower_v,upper_ts,upper_v=self.nearest_timestamps(ts)
            print(lower_ts,lower_v,upper_ts,upper_v)
            if lower_ts is None or lower_v is None or \
                upper_ts is None or upper_v is None: 
                return None
            else:
                interval_ts=upper_ts-lower_ts
                ts_proportion=(ts-lower_ts)/(interval_ts)
                interval_v=upper_v-lower_v
                v=lower_v+(interval_v)*(ts_proportion)
                return v
            
    
    def plot(self):
        "a simple plot of the data"
        self.series.plot(style='-o')


class Variable():
    """Represents a variable which holds time series data
    
    """
    
    def __init__(self,
                 name='',
                 ts=None,
                 units=''):
        self.name=name
        self.ts=ts
        self.units=units


    def __repr__(self):
        d={
            'name':self.name,
            'ts':self.ts,
            'units':self.units
            }
        return 'Variable({})'.format(d)


    def json(self):
        d={
            'name':self.name,
            'units':self.units
            }
        if self.ts:
            d['ts']=self.ts.json()
        return d


    def plot(self,ax=None):
        if not ax:
            fig=plt.figure(figsize=(13,4))
            ax=fig.add_axes([0, 0, 1, 1])
        self.ts.plot(ax,
                     self.name,
                     self.units)
        
        
    def plot_colormap(self,ax=None):
        if not ax:
            fig=plt.figure(figsize=(13,4))
            ax=fig.add_axes([0, 0, 1, 1])
        im=self.ts.plot_colormap(ax)
        cbar=plt.colorbar(im, ax=ax)
        st='{} ({})'.format(self.name, self.units)
        cbar.ax.set_ylabel(st)


    def hist(self,ax=None,bins=None):
        if not ax:
            fig=plt.figure(figsize=(13,4))
            ax=fig.add_axes([0, 0, 1, 1])
        self.ts.hist(ax,
                     bins,
                     self.name,
                     self.units)
        
        
    def chist(self,ax=None,bins=None):
        if not ax:
            fig=plt.figure(figsize=(13,4))
            ax=fig.add_axes([0, 0, 1, 1])
        self.ts.chist(ax,
                     bins,
                     self.name,
                     self.units)


from pprint import pprint
        
if __name__=='__main__':
    
    from bim_graph import BimGraph
    
    bim=BimGraph()
    bim.read_pickle(r'../tests/timeseries/refit_ext_temp.pickle')
    
    climate=bim.Climate[0]
    sensor=[n for n in climate.Sensor if n.air_temperature][0]
    var=sensor.air_temperature
    print(var)
    
    
    
    


