# -*- coding: utf-8 -*-

"""This module contains a number of 'value' classes

The value classes are used to represent ???

"""

import pandas as pd
import numpy as np
import random


class NumpyRandomNormal():
    """A class that represents the numpy.random.normal function
    """
    
    def __init__(self,
                 loc=0.0,
                 scale=1.0,
                 min1=None,
                 max1=None):
        self.loc=loc
        self.scale=scale
        self.min1=min1
        self.max1=max1
        
        
    def sample(self):  # NEEDS CHECKING THAT AN SD OF 1 * MULTIPLER = SD OF MULTIPLIER
        while True:
            n=np.random.normal(loc=0,scale=1)
            v=self.loc+self.scale*n
            if self.min1 and v<=self.min1:
                continue
            if self.max1 and v>=self.max1:
                continue
            return v
            
        
    def __repr__(self):
        return \
            'NumpyRandomNormal(loc={},scale={},min1={},max1={})'.format(self.loc,
                                                                        self.scale,
                                                                        self.min1,
                                                                        self.max1
                                                                        )



class RandomChoice():
    """A class that represents the random.choice function
    """
    
    def __init__(self, seq=None):
        self.seq=seq
        
        
    def sample(self):
        if self.seq:
            return random.choice(self.seq)
        else:
            return None
        
        
    def __repr__(self):
        return 'RandomChoice({})'.format(self.seq)




### TESTS ###


#if __name__=='__main__':
#       
#    import subprocess
#    
#    def run_test(fp):
#        print('run_test: fp={}'.format(fp))
#        p=subprocess.run(['python.exe',fp],
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.PIPE)
#        print(p.stderr.decode())
#        print(p.stdout.decode())
#    
#    fp=r'../tests/test_NumpyRandomNormal.py'
#    run_test(fp)
    

    
    
    
    
    
    
    
    