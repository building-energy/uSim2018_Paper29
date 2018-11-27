# -*- coding: utf-8 -*-

import subprocess
import os
import copy
import shutil
import datetime

try:
    from .eso_graph import EsoGraph
except ImportError:
    from eso_graph import EsoGraph

try:
    from .bim_to_idf_map import BimToIdfMap
except ImportError:
    from bim_to_idf_map import BimToIdfMap

try:
    from .eso_to_bim_map import EsoToBimMap
except ImportError:
    from eso_to_bim_map import EsoToBimMap
    
try:
    from .gbxml_to_bim_map import GbxmlToBimMap
except ImportError:
    from gbxml_to_bim_map import GbxmlToBimMap

class EnergyPlusModel():
    "A model object for running EnergyPlus simulations"
    
    def __init__(self):
        self.input_idf=None  # an IdfGraph object
        self.input_epw=None  # the weather file name with no extension
        self.input_bim=None
        self.input_gbxml=None
        self.simulation_folder=''
        self.output_err=None
        self.output_rdd=None
        self.output_eso=None  # an EsoGraph object
        self.output_bim=None
    
    
    def run_gbxml(self,
                  output_variables=None):
        """Runs the EnergyPlus model based on a GbxmlGraph
        
        Requires:
            - self.input_gbxml (GbxmlGraph)
            - self.input_epw (str): no extension
            - self.simulation_folder (str)
            
        Sets:
            - self.output_err
            - self.output_rdd
            - self.output_eso
            - self.output_bim
            
        """
        
        #CONVERT GBXML TO BIM
        o=GbxmlToBimMap()
        o.input_gbxml=self.input_gbxml
        o.run()
        self.bim=o.output_bim
        
        #RUN ENERGYPLUS
        self.run_bim(output_variables=output_variables)
        
        return
    
    
    def run_bim(self,
                output_variables=None):
        """Runs the EnergyPlus model based on a BimGraph
        
        Requires:
            - self.bim (BimGraph)
            - self.input_epw (str): no extension
            - self.simulation_folder (str)
            
        Sets:
            - self.output_err
            - self.output_rdd
            - self.output_eso
            - self.output_bim        
            
        """
        
        #CONVERT BIM TO IDF
        o=BimToIdfMap()
        o.input_bim=self.bim
        o.run()
        self.input_idf=o.output_idf
        
        #RUN ENERGYPLUS
        result=self.run_idf(output_variables=output_variables)
        if not result: return
        
        #READ ESO FILE
        eso=EsoGraph()
        folder=os.path.abspath(self.simulation_folder)
        fp=os.path.join(folder,'eplusout.eso')
        eso.read_eso(fp)
        
        #MAP ESO TO BIM
        o1=EsoToBimMap()
        o1.bim=self.bim
        o1.input_eso=eso
        o1.run()
        self.output_bim=o1.bim
    
    
    def run_idf(self,
                output_variables=None):
        """Runs the EnergyPlus model based on an idf
        
        Requires:
            self.input_idf (IdfGraph)
            self.input_epw (str): 
            self.simulation_folder (str)
            
        Sets:
            - self.output_err
            - self.output_rdd
        
        """
        idf=copy.deepcopy(self.input_idf)
        
        #ADD OUTPUT VARIABLES
        if not output_variables:
            output_variables=\
                ['Site Outdoor Air Drybulb Temperature',
                 'Zone Mean Air Temperature']
        for variable_name in output_variables:
            idf.add_output_variable(variable_name=variable_name)
        
        #SET ENERGYPLUS EXE FILEPATH
        epexe_fp=r'C:\EnergyPlusV8-9-0\EnergyPlus'
        
        #CREATE THE SIMULATION FOLDER IF IT DOESN'T EXIST
        folder=os.path.abspath(self.simulation_folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        expidf_fp=os.path.join(folder,'eplusout.expidf')
        if os.path.isfile(expidf_fp):
            os.remove(expidf_fp) #  needed as sometimes this isn't recreated and an old version is used??
        
        
        #SAVE THE IDF FILE IN SIMULATION_FOLDER
        file='in.idf'
        idf_fp=os.path.join(folder,file)
        idf.write_idf(idf_fp)
        
        #SET ENERGYPLUS WEATHER FILE NAME 
        epw_fp=self.input_epw
        
        #RUN ENERGYPLUS
        self.run_energyplus(epexe_fp=epexe_fp,
                            idf_fp=idf_fp,
                            epw_fp=epw_fp,
                            out_fp=folder,
                            )
        
        #READ ERR FILE
        fp=os.path.join(folder,'eplusout.err')
        if os.path.isfile(fp):
            with open(fp,'r') as f:
                self.output_err=f.read()
        
        #RETURNS FALSE IF PROCESS TERMINATED
        if 'Terminated' in self.output_err:
            print(self.output_err)
            return False
        
        #READ RDD FILE
        fp=os.path.join(folder,'eplusout.rdd')
        if os.path.isfile(fp):
            with open(fp,'r') as f:
                self.output_rdd=f.read()
        
        return True
                
    
    def run_energyplus(self,
                       epexe_fp,
                       out_fp,
                       idf_fp,
                       epw_fp
                       ):
        """Runs the EnergyPlus software
        
        Arguments:
            - epexe_fp (str): the absolute filepath of the 'energyplus.exe' file - excluding the extension
            - out_fp (str): the filepath of the output folder
            - idf_fp (str): the filepath of the idf file - including the extension
            - epw_fp (str): the filepath of the epw file - including the extension
        
        """
        #print(epexe_fp,out_fp,idf_fp,epw_fp)
        
        
        #CREATES THE 'OUT' FOLDER IF IT DOESN'T EXIST
        if not os.path.isdir(out_fp):
            os.mkdir(out_fp)
        
        #COPY IDF TO 'IN.IDF' FILE IN THE OUT FOLDER
        try:
            shutil.copyfile(idf_fp,
                            os.path.join(out_fp,'in.idf'))
        except shutil.SameFileError:
            pass
        
        #RUN EXPAND OBJECTS
        cwd=os.getcwd()
        os.chdir(out_fp)
        os.system(r'C:\EnergyPlusV8-9-0\ExpandObjects')
        os.chdir(cwd)
        idf_fp_new=os.path.join(out_fp,'expanded.idf')
        
        #RUN ENERGYPLUS VIA OS.SYSTEM
        l=[epexe_fp,
           '-r',
           '-c',
           '-d','"'+out_fp+'"',
           '-w','"'+epw_fp+'"',
           '"'+idf_fp_new+'"']
        
        st=' '.join(l)
        
        print(st)
        
        os.system(st)
        
        #READ ERR FILE
        fp=os.path.join(out_fp,'eplusout.err')
        if os.path.isfile(fp):
            with open(fp,'r') as f:
                self.output_err=f.read()
        
        return
    
        
# tests

if __name__=='__main__':
    from pprint import pprint
    from idf_graph import IdfGraph
    from bim_graph import BimGraph
    from gbxml_graph import GbxmlGraph
    
    print('TEST-EnergyplusModel')
    o=EnergyPlusModel()
    epexe_fp=r'C:\EnergyPlusV8-9-0\EnergyPlus'
    #idf_fp=r'../tests/energyplus_model\sim_epJSON\1ZoneUncontrolled.epJSON'
    #idf_fp=r'../tests/energyplus_model\sim_epJSON\in.epJSON'
    #idf_fp=r'../tests/energyplus_model\sim_epJSON\detached_house.epJSON'
    idf_fp=r'../tests/energyplus_model\detached_house.idf'
    epw_fp=r'C:\EnergyPlusV8-9-0\WeatherData\GBR_Birmingham.035340_IWEC.epw'
    out_fp=r'../tests/energyplus_model\sim'
    #out_fp=r'../tests/energyplus_model\sim_epJSON'
    o.run_energyplus(epexe_fp=epexe_fp,
                     idf_fp=idf_fp,
                     epw_fp=epw_fp,
                     out_fp=out_fp)
    #print(o.output_err)
    
    
#    # IdfGraph
#    idf=IdfGraph()
#    idf.read_idf(r'../tests/energyplus_model/detached_house.idf')
#    
#    o=EnergyPlusModel()
#    o.input_idf=idf
#    o.simulation_folder=r'../tests/energyplus_model/sim'
#    o.input_epw=r'C:\EnergyPlusV8-9-0\WeatherData\GBR_Birmingham.035340_IWEC.epw'
#    #o.run_idf()    
#    
#    # BimGraph
#    bim=BimGraph()
#    bim.read_pickle(r'../tests/energyplus_model/detached_house.pickle')
#    
#    o1=EnergyPlusModel()
#    o1.bim=bim
#    o1.simulation_folder=r'../tests/energyplus_model/sim'
#    o1.input_epw=r'C:\EnergyPlusV8-9-0\WeatherData\GBR_Birmingham.035340_IWEC.epw'
#    o1.run_bim()
#    o1.bim.write_pickle(r'../tests/energyplus_model/bim.pickle')    
#    
#    print('TEST_RUN')
#    o.simulation_folder=r'../tests/energyplus_model/sim'
#    o.input_epw=r'GBR_Birmingham.035340_IWEC'
#    o.run_idf()
#    
#    bim=BimGraph()
#    bim.read_pickle(r'../tests/energyplus_model/detached_house.pickle')
#    o1=EnergyPlusModel()
#    o1.simulation_folder=r'../tests/energyplus_model/sim'
#    o1.input_epw=r'GBR_Birmingham.035340_IWEC'
#    o1.input_bim=bim
#    o1.run_bim()
#    print(o1.output_bim)
#    o1.output_bim.write_pickle(r'../tests/energyplus_model/bim.pickle')
#    
#    
#    bim=BimGraph()
#    bim.read_pickle(r'../tests/energyplus_model/detached_house.pickle')
#    o1=EnergyPlusModel()
#    o1.simulation_folder=r'../tests/energyplus_model/sim'
#    o1.input_epw=r'GBR_Birmingham.035340_IWEC'
#    o1.input_bim=bim
#    o1.run_bim()
#    print(o1.output_bim)
#    o1.output_bim.write_pickle(r'../tests/energyplus_model/bim2.pickle')
    
#    gbxml=GbxmlGraph()
#    gbxml.read_xml(r'../tests/energyplus_model/detached_house.gbxml')
#    o1=EnergyPlusModel()
#    o1.simulation_folder=r'../tests/energyplus_model/sim'
#    o1.input_epw=r'GBR_Birmingham.035340_IWEC'
#    o1.input_gbxml=gbxml
#    o1.run_gbxml()
#    print(o1.output_bim)
#    o1.output_bim.write_pickle(r'../tests/energyplus_model/bim3.pickle')
#    
#    gbxml=GbxmlGraph()
#    gbxml.read_xml(r'../tests/energyplus_model/detached_house.gbxml')
#    o1=EnergyPlusModel()
#    o1.simulation_folder=r'../tests/energyplus_model/sim'
#    o1.input_epw=r'GBR_Birmingham.035340_IWEC'
#    o1.input_gbxml=gbxml
#    o1.run_gbxml()
#    print(o1.output_bim)
#    o1.output_bim.write_pickle(r'../tests/energyplus_model/bim4.pickle')
#    
    
    #print(o.output_eso.json()[0])
    #print(o.output_err)
    
    
    
    #print(o.output_err)
    #print(o.output_rdd)
    
#    l=o.output_idf.json()
##    l=[x for x in o.output_bim.json() if 'OpaqueMaterial' in x['labels']]
#    #pprint(l)
#    
#    st=o.output_idf.idf_string()
#    print(st)
#    o.output_idf.write_idf(r'../tests/bim_to_idf_map/test.idf')








#        #RENAME EPLUSOUT FILES
#        idf_name,idf_extension=os.path.splitext(idf_filename)
#        for filename in os.listdir(out_fp):
#            name, extension=os.path.splitext(filename)
#            fp=os.path.join(out_fp,filename)
#            if name=='eplusout':
#                os.rename(fp,os.path.join(out_fp,idf_name+extension))
                
    
        #MOVE IDF FILE TO OUT FOLDER
#        idf_dir,idf_filename=os.path.split(idf_fp)
#        fp=os.path.join(out_fp,idf_filename)
#        try:
#            shutil.copyfile(idf_fp,fp)
#        except shutil.SameFileError:
#            pass

    