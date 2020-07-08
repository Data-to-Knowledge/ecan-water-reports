# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 16:27:09 2017

@author: MichaelEK
"""
import geopandas as gpd
import pandas as pd
import os
from util import grp_ts_agg, tsreg, getPolyCoords
import shutil
from gistools.vector import multipoly_to_poly, xy_to_gpd
from datetime import date
from scipy.stats import rankdata
from numpy import nan
from warnings import filterwarnings
from pdsql import mssql
from pyhydrotel import get_ts_data

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, CategoricalColorMapper, CustomJS, renderers, annotations
from bokeh.palettes import brewer
from bokeh.models.widgets import Select
from bokeh.layouts import column
from bokeh.io import save

import parameters as param

pd.options.display.max_columns = 10

##################################################
#### Read in data

print('Reading in the data')

### gw
#gw_sites = read_file(join(base_dir, gw_sites_shp))
gw_zones = gpd.read_file(os.path.join(param.base_dir, param.input_dir, param.gw_poly_shp))[['ZONE_NAME', 'geometry']]

gw_zones = gw_zones.rename(columns={'ZONE_NAME': 'zone'})
#gw_zones['mtype'] = 'gw'

# well_depths = pd.read_csv(os.path.join(param.base_dir, param.input_dir, param.well_depth_csv)).set_index('site')

well_depths = mssql.rd_sql(param.wells_server, param.wells_database, param.well_depth_table, ['well_no', 'depth']).drop_duplicates('well_no')
well_depths = well_depths[well_depths['depth'].notnull()]
well_depths.rename(columns={'depth': 'well_depth'}, inplace=True)

well_screens = mssql.rd_sql(param.wells_server, param.wells_database, param.well_screen_table, ['well_no', 'top_screen'], where_in={'screen_no': [1]}).drop_duplicates('well_no')

##################################################
#### Process well depth catergories
well_info = pd.merge(well_depths, well_screens, on='well_no', how='left')

well_info['depth'] = 'Shallow'
well_info.loc[well_info['top_screen'] >= 30, 'depth'] = 'Deep'
well_info.loc[well_info['top_screen'].isnull() & (well_info['well_depth'] >= 30), 'depth'] = 'Deep'

well_depths = well_info[['well_no', 'depth']].rename(columns={'well_no': 'site'}).set_index('site')

#################################################
#### Select sites

### GW
sites = mssql.rd_sql(param.hydro_server, param.hydro_database, param.sites_table, ['ExtSiteID', 'NZTMX', 'NZTMY', 'CwmsName'])
sites.rename(columns={'ExtSiteID': 'site'}, inplace=True)

sites = sites[sites.site.isin(well_depths.index)]

## Manual data
mgw1 = mssql.rd_sql_ts(param.hydro_server, param.hydro_database, param.ts_table, 'ExtSiteID', 'DateTime', 'Value', where_in={'DatasetTypeID': [13]}).reset_index()
mgw1.rename(columns={'ExtSiteID': 'site', 'DateTime': 'time', 'Value': 'data'}, inplace=True)

mgw1 = mgw1[mgw1.site.isin(sites.site)]

## Recorder data
# hy1 = get_ts_data(param.hydrotel_server, param.hydrotel_database, ['water level', 'adjusted water level'], sites.site.tolist(), resample_code='D').reset_index()
# rgw1 = hy1.sort_values('MType').drop_duplicates(['ExtSiteID', 'DateTime']).drop('MType', axis=1)
# rgw1.rename(columns={'ExtSiteID': 'site', 'DateTime': 'time', 'Value': 'data'}, inplace=True)

# rgw1 = mssql.rd_sql_ts(param.hydro_server, param.hydro_database, param.ts_table, 'ExtSiteID', 'DateTime', 'Value', where_in={'DatasetTypeID': [10]}).reset_index()
# rgw1.rename(columns={'ExtSiteID': 'site', 'DateTime': 'time', 'Value': 'data'}, inplace=True)
#
# rgw1 = rgw1[rgw1.site.isin(sites.site)]

## Prioritise recorder data
# mgw1 = mgw1[~mgw1.site.isin(rgw1.site.unique())].copy()

## Combine
# gw1 = pd.concat([rgw1, mgw1]).drop_duplicates(['site', 'time'])
gw1 = mgw1.copy()

#################################################
#### Run monthly summary stats

print('Processing past data')

### Filter sites
count0 = gw1.copy()
count0['month'] = gw1.time.dt.month
count0['year'] = gw1.time.dt.year
count1 = count0.drop_duplicates(['site', 'year', 'month']).groupby('site').data.count()

start_date0 = gw1.groupby('site').time.first()
end_date1 = gw1.groupby('site').time.last()

now1 = pd.to_datetime(param.date_now) + pd.DateOffset(days=param.add_days)
start_date1 = now1 - pd.DateOffset(months=121) - pd.DateOffset(days=now1.day - 1)
start_date2 = now1 - pd.DateOffset(months=1) - pd.DateOffset(days=now1.day - 1)

sites1 = sites[sites.site.isin(count1[(count1 >= 120) & (end_date1 >= start_date2) & (start_date0 <= start_date1)].index)]

uw1 = sites[sites.CwmsName.isin(['Upper Waitaki']) & sites.site.isin(count1[(count1 >= 80) & (end_date1 >= start_date2) & (start_date0 <= start_date1)].index)]

sites2 = pd.concat([sites1, uw1]).drop_duplicates()

gw_sites = xy_to_gpd(['site', 'CwmsName'], 'NZTMX', 'NZTMY', sites2)

gw2 = gw1[gw1.site.isin(gw_sites.site)].copy()

### Extract Site locations
gw_sites.to_file(os.path.join(param.base_dir, param.output_dir, param.gw_sites_shp))

### Combine the sites with the polygons
gw_site_zone = gw_sites.drop(['geometry'], axis=1)
gw_site_zone.rename(columns={'CwmsName': 'zone'}, inplace=True)

### Monthly interpolations
if param.interp:
    ## Estimate monthly means through interpolation
    day1 = grp_ts_agg(gw2, 'site', 'time', 'D').mean().unstack('site')
    day2 = tsreg(day1, 'D', False)
    day3 = day2.interpolate(method='time', limit=40)
    mon_gw1 = day3.resample('M').median().stack().reset_index()
else:
    mon_gw1 = grp_ts_agg(gw2, 'site', 'time', 'M').median().reset_index()

## End the dataset to the lastest month
end_date = now1 - pd.DateOffset(days=now1.day - 1)
mon_gw1 = mon_gw1[mon_gw1.time < end_date].copy()

## Assign month
mon_gw1['mon'] = mon_gw1.time.dt.month

##############################################
#### Run the monthly stats comparisons

print('Calculating the percentiles')

hy_gw0 = mon_gw1.copy()
hy_gw0['perc'] = (hy_gw0.groupby(['site', 'mon'])['data'].transform(lambda x: (rankdata(x)-1)/(len(x)-1)) * 100).round(2)


###############################################
#### Pull out recent monthly data

start_date = now1 - pd.DateOffset(months=param.n_previous_months) - pd.DateOffset(days=now1.day - 1)

print('start date: ' + str(start_date), 'and date: ' + str(end_date))

### selection

hy_gw = hy_gw0[(hy_gw0.time >= start_date)].copy()

### Convert datetime to year-month str
hy_gw['time'] = hy_gw.time.dt.strftime('%Y-%m')

##############################################
#### Calc zone stats and apply categories

perc_site_zone = pd.merge(hy_gw, gw_site_zone, on='site')
perc_zone = perc_site_zone.groupby(['zone', 'time'])['perc'].mean()

prod1 = [gw_zones.zone.unique(), perc_zone.reset_index().time.unique()]
mindex = pd.MultiIndex.from_product(prod1, names=['zone', 'time'])
blank1 = pd.Series(nan, index=mindex, name='temp')
zone_stats2 = pd.concat([perc_zone, blank1], axis=1).perc
zone_stats2[zone_stats2.isnull()] = -1

cat_val_lst = [-10, -0.5, 10, 25, 75, 90, 100]
cat_name_lst = ['No data', 'Very low', 'Below average', 'Average', 'Above average', 'Very high']

cat1 = pd.cut(zone_stats2, cat_val_lst, labels=cat_name_lst).astype('str')
cat1.name = 'category'
cat2 = pd.concat([zone_stats2, cat1], axis=1)
cat3 = cat2.sort_values('perc', ascending=False).category

################################################
#### Output stats

print('Exporting results to csv')

ts_out1 = hy_gw.loc[:, ['site', 'time', 'perc']].copy()
ts_out2 = ts_out1.pivot_table('perc', 'site', 'time').round(2)

stats1 = mon_gw1.groupby('site')['data'].describe().round(2)
ts_out3 = pd.concat([ts_out2, stats1], axis=1, join='inner')
well_depths1 = well_depths.loc[ts_out3.index]
ts_out4 = pd.concat([ts_out3, well_depths1], axis=1).reset_index()

gw_sites_ts = gw_sites.merge(ts_out4, on='site')
gw_sites_ts.crs = gw_sites.crs
gw_sites_ts.to_file(os.path.join(param.base_dir, param.output_dir, param.gw_sites_ts_shp))

ts_out10 = hy_gw0.loc[:, ['site', 'time', 'perc']].copy()
ts_out10['time'] = ts_out10['time'].dt.date.astype(str)
ts_out10['perc'] = ts_out10['perc'].round(2)
ts_out10.to_csv(os.path.join(param.base_dir, param.output_dir, param.gw_sites_ts_csv), header=True, index=False)


#################################################
#### Plotting

print('Creating the plot')

### Extract x and y data for plotting

zones1 = multipoly_to_poly(gw_zones)

zones1['x'] = zones1.apply(getPolyCoords, coord_type='x', axis=1)
zones1['y'] = zones1.apply(getPolyCoords, coord_type='y', axis=1)

zones2 = zones1.drop('geometry', axis=1)

### Combine with time series data
data1 = pd.merge(cat1.unstack('time').reset_index(), zones2, on=['zone'])
time_index = hy_gw.time.unique().tolist()
data1['cat'] = data1[time_index[-1]]

### Extract the mtype dataframes
gw_b = data1.copy()

gw_source = ColumnDataSource(gw_b)
time_source = ColumnDataSource(pd.DataFrame({'index': time_index}))

### Set up plotting parameters
c1 = brewer['RdBu'][5]
grey1 = brewer['Greys'][7][5]

factors = cat_name_lst[::-1]
color_map = CategoricalColorMapper(factors=factors, palette=[c1[0], c1[1], c1[2], c1[3], c1[4], grey1])

### Set up dummy source for the legend
dummy_b = gw_b[['zone', 'cat', 'x', 'y']].sort_values('zone')
dummy_b.loc[:, 'cat'].iloc[0:len(factors)] = factors
dummy_source = ColumnDataSource(dummy_b)

TOOLS = "pan,wheel_zoom,reset,hover,save"

w = 700
h = w

bokeh_gw_cwms_html = os.path.join(param.base_dir, param.bokeh_dir, param.today_gw_cwms_html)
output_file(bokeh_gw_cwms_html)

## dummy figure - for legend consistency
p0 = figure(title='dummy Index', tools=[], height=h, width=w)
p0.patches('x', 'y', source=dummy_source, fill_color={'field': 'cat', 'transform': color_map}, line_color="black", line_width=1, legend='cat')
p0.renderers = [i for i in p0.renderers if (type(i) == renderers.GlyphRenderer) | (type(i) == annotations.Legend)]
p0.renderers[1].visible = False

## Figure 3 - GW
p3 = figure(title='Groundwater Level Index', tools=TOOLS, active_scroll='wheel_zoom', plot_height=h, plot_width=w)
p3.patches('x', 'y', source=gw_source, fill_color={'field': 'cat', 'transform': color_map}, line_color="black", line_width=1, legend='cat')
p3.renderers.extend(p0.renderers)
p3.legend.location = 'top_left'

hover3 = p3.select_one(HoverTool)
hover3.point_policy = "follow_mouse"
hover3.tooltips = [("Category", "@cat"), ("Zone", "@zone")]

callback3 = CustomJS(args=dict(source=gw_source), code="""
    var data = source.data;
    var f = cb_obj.value;
    source.data.cat = data[f];
    source.change.emit();
""")

select3 = Select(title='Month', value=time_index[-1], options=time_index)
select3.js_on_change('value', callback3)

layout3 = column(p3, select3)

save(layout3)

#############################################
### Make html copy without date in filename

bokeh_subregion_html1 = os.path.join(os.path.split(bokeh_gw_cwms_html)[0], param.base_gw_cwms_html)

shutil.copy(bokeh_gw_cwms_html, bokeh_subregion_html1)


#############################################
#### Print where results are saved

#print('########################')
#
#print('shapefile results were saved here: ' + os.path.join(param.base_dir, param.input_dir, param.gw_sites_ts_shp))
#print('csv results were saved here: ' + os.path.join(param.base_dir, param.input_dir, param.gw_sites_ts_csv))
#print('The plot was saved here: ' + os.path.join(param.base_dir, param.input_dir, param.today_gw_cwms_html))
