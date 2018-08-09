# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 10:19:05 2018

@author: MichaelEK
"""
from git import Repo
import os
import parameters as param

################################
### Run mapping scripts

print('precip and sw maps')
import water_report_precip_sw_gw as map1


################################
### Modify the index.rst

index_rst = r'sphinx\source\index.rst'
index_rst_path = os.path.join(param.base_dir, index_rst)

with open(index_rst_path, 'r+') as r1:
    lines = r1.readlines()
    lines[8] = param.date_now + '\n'

with open(index_rst_path, 'w+') as w1:
    w1.writelines(lines)


################################
### Commit and push to github

repo = Repo(param.base_dir)

file_list = [map1.bokeh_catch_html1, map1.bokeh_subregion_html1, map1.bokeh_catch_html, map1.bokeh_subregion_html, map1.ts_out_path, index_rst_path]

repo.index.add(file_list)
repo.index.commit('update')
origin = repo.remote('origin')
origin.push()

