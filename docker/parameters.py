# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 09:29:52 2018

@author: michaelek
"""
import os
from configparser import ConfigParser
from datetime import date

#####################################
### Parameters

## Generic
base_dir = os.path.realpath(os.path.dirname(__file__))

ini1 = ConfigParser()
ini1.read([os.path.join(base_dir, os.path.splitext(__file__)[0] + '.ini')])

py_file = 'main.py'

base_dir = os.path.split(os.path.realpath(os.path.dirname(__file__)))[0]

input_dir = 'input_data'

hydro_server = str(ini1.get('Input', 'hydro_server'))
hydro_database = str(ini1.get('Input', 'hydro_database'))
ts_table = str(ini1.get('Input', 'ts_table'))
sites_table = 'ExternalSite'

hydrotel_server = str(ini1.get('Input', 'hydrotel_server'))
hydrotel_database = str(ini1.get('Input', 'hydrotel_database'))

sw_poly_shp = str(ini1.get('Input', 'sw_poly_shp'))
precip_poly_shp = str(ini1.get('Input', 'precip_poly_shp'))
rec_catch_shp = str(ini1.get('Input', 'rec_catch_shp'))
view_bound_shp = str(ini1.get('Input', 'view_bound_shp'))
precip_site_shp = str(ini1.get('Input', 'precip_site_shp'))
pot_sw_site_list_csv = str(ini1.get('Input', 'pot_sw_site_list_csv'))

gw_poly_shp = str(ini1.get('Input', 'gw_poly_shp'))
well_depth_csv = str(ini1.get('Input', 'well_depth_csv'))
upper_waitaki_shp = str(ini1.get('Input', 'upper_waitaki_shp'))

interp = True

qual_codes = [10, 18, 20, 30, 50, 11, 21, 40]

n_previous_months = int(ini1.get('Input', 'n_previous_months'))
add_days = int(ini1.get('Input', 'add_days'))

month_names = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August', 'Sept', 'Oct', 'Nov', 'Dec']

lon_zone_names = {'L': 'Lowlands', 'F': 'Foothills', 'M': 'Mountains', 'BP': 'Banks Peninsula'}

### Output
output_dir = 'output_results'
bokeh_dir = r'sphinx\source\bokeh_html'
date_now = str(date.today())

ts_out_csv = 'ts_out_perc_' + date_now + '.csv'

gw_sites_shp = 'gw_sites_' + date_now + '.shp'
all_gw_sites_shp = 'all_discrete_gw_sites_' + date_now + '.shp'
gw_sites_ts_shp = 'gw_sites_perc_' + date_now + '.shp'
gw_sites_ts_csv = 'gw_sites_perc_' + date_now + '.csv'

## plots


## plots
base_precip_sw_subregion_name = 'precip_sw'

base_precip_sw_subregion_html = base_precip_sw_subregion_name + '.html'
today_precip_sw_subregion_html = base_precip_sw_subregion_name + '_' + date_now + '.html'

base_sw_catch_name = 'sw_catch'

base_sw_catch_html = base_sw_catch_name + '.html'
today_sw_catch_html = base_sw_catch_name + '_' + date_now + '.html'

today_gw_cwms_html = 'gw_cwms_' + date_now + '.html'
base_gw_cwms_html = 'gw_cwms.html'
