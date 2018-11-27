# uSIM_2018/analysis

This folder contains the folders and code used for the analysis.

The folders are numbered and this gives the order in which the analysis is done. Some folders contain data files 
and some contains the analysis code, written as Jupyter notebooks.

The analysis uses the [openbuilding][ob] Python package.

The details of the analysis workflow is:

- **1_file-original_gbXML**: this contains a gbXML file which describes a detached house. This is the starting point of the analysis
the remaining steps modify this file, run simuations, and analyse the results.
- **2_code-gen_gbXML_files**: this contains a Jupyter notebook which modifies the original gbXML file. The file is modified by altering
the orientation from 0 to 355 degrees in steps of 5 degrees.
- **3_files-new_gbXML**: this contains the modified gbXML files.
- **4_code-map_gbxml_to_bim**:
- **5_files-bim_pre_sim**:
- **6_code-run_energyplus**:
- **7_files-idf**:
- **8_files-bim_post_sim**:
- **9_analysis**:


[ob]: https://openbuilding.github.io/
