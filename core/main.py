# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 10:19:05 2018

@author: MichaelEK
"""
import pandas as pd
from pdsql.mssql import to_mssql
from git import Repo
from datetime import datetime
import os
import parameters as param

today = datetime.today()
today1 = str(today.date())
today2 = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
today3 = str(today.strftime('%Y-%m-%d %H:%M:%S'))

try:

    ################################
    ### Run mapping scripts

    print('precip and sw maps')
    import water_report_precip_sw_gw as map1

    print('gw map')
    import water_report_gw as map2

    print('lowflow restrictions')
    import lowflow_restrictions as lfr

    ################################
    ### Modify the index.rst

    index_rst = r'sphinx\source\index.rst'
    index_rst_path = os.path.join(param.base_dir, index_rst)

    with open(index_rst_path, 'r') as r1:
        lines = r1.readlines()
        lines[8] = param.date_now + '\n'

    with open(index_rst_path, 'w') as w1:
        w1.writelines(lines)


    ################################
    ### Commit and push to github

    repo = Repo(param.base_dir)

    file_list = [map1.bokeh_catch_html1, map1.bokeh_subregion_html1, map1.bokeh_catch_html, map1.bokeh_subregion_html, map1.ts_out_path, index_rst_path, map2.bokeh_gw_cwms_html, map2.bokeh_subregion_html1]

    repo.index.add(file_list)
    repo.index.commit('update')
    origin = repo.remote('origin')
    origin.push()

    ###############################
    ### Log

#    log1 = pd.DataFrame([[today3, 'Freshwater Maps', 'pass', 'all good', str(map1.start_date), today2]], columns=['Time', 'HydroTable', 'RunResult', 'Comment', 'FromTime', 'RunTimeEnd'])
#    to_mssql(log1, param.hydro_server, param.hydro_database, 'ExtractionLog')
except Exception as err:
    err1 = err
    print(err1)
#    today2 = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
#    log2 = pd.DataFrame([[today2, 'Freshwater Maps', 'fail', str(err1)[:299], str(map1.start_date), today2]], columns=['Time', 'HydroTable', 'RunResult', 'Comment', 'FromTime', 'RunTimeEnd'])
#    to_mssql(log2, param.hydro_server, param.hydro_database, 'ExtractionLog')
