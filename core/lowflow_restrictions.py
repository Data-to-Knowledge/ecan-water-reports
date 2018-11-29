# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 12:46:41 2018

@author: MichaelEK
"""
import numpy as np
from os import path
import pandas as pd
from pdsql.mssql import rd_sql
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.ticker as plticker

plt.ioff()

loc = plticker.MaxNLocator(integer=True)

datetime1 = pd.Timestamp.today()
#date1 = pd.Timestamp(datetime1.date())

#####################################
### Parameters

server = 'SQL2012test01'
database = 'Hydro'
table = 'LowFlowRestrSite'
site_table = 'ExternalSite'

#cwms_gis = {'server': 'SQL2012PROD05', 'database': 'GIS', 'table': 'CWMS_NZTM_ZONES', 'col_names': ['ZONE_NAME'], 'rename_cols': ['cwms'], 'geo_col': True}
bad_sites = {'66101': '14240260', '65104': '165104', '69650': '696501'}

irr_mons1 = [10, 11, 12]
irr_mons2 = [1, 2, 3, 4]

include_flow_methods = ['Correlated from Telem', 'Gauged', 'Telemetered', 'Visually Gauged', 'GW manual']

##color palettes
full_color = sns.color_palette('Blues')
partial_color = sns.color_palette('Greens')
no_color = sns.color_palette('Greys')

export_path = r'E:\ecan\shared\projects\mon_water_report\plots'
#export_sel2 = 'lowflow_restr_2017-10-01.csv'

####################################
### Set up time ranges

mon_now = datetime1.month
year_now = datetime1.year

if mon_now in irr_mons1:
    from_date = '{year}-10-01'.format(year=year_now)
elif mon_now in irr_mons2:
    from_date = '{year}-10-01'.format(year=year_now - 1)
else:
    from_date = '{year}-05-01'.format(year=year_now)

end_mon_now = datetime1 - pd.DateOffset(months=1) + pd.tseries.offsets.MonthEnd(0)
to_date = str(end_mon_now.date())
#to_date = '2018-11-30'

export_name_fancy = '{start}_{end}_restrictions_fancy.png'.format(start=from_date, end=to_date)
export_name = '{start}_{end}_restrictions.png'.format(start=from_date, end=to_date)
export_man_calc_sites = '{start}_{end}_lowflow_sites.csv'.format(start=from_date, end=to_date)

####################################
### extract data

#cwms = rd_sql(**cwms_gis)

lowflow1 = rd_sql(server, database, table, where_col={'site_type': ['LowFlow']}, from_date=from_date, to_date=to_date, date_col='date')
lowflow1['date'] = pd.to_datetime(lowflow1['date'])
lowflow2 = lowflow1[lowflow1.flow_method.isin(include_flow_methods)].copy()

sites1 = lowflow2.site.unique().tolist()
sites1.extend(list(bad_sites.keys()))

sites = rd_sql(server, database, site_table, ['ExtSiteID', 'CwmsName'], where_col={'ExtSiteID': sites1}, rename_cols=['site', 'cwms'])

bad_ones = sites[sites.site.isin(list(bad_sites.keys()))].copy()
bad_ones.replace({'site': bad_sites}, inplace=True)

sites2 = pd.concat([sites, bad_ones])

## Other - unused for now - but might later
#site_restr1 = lowflow2.groupby(['site', 'restr_category'])['crc_count'].count()
#site_restr1.name = 'count'
#max_days = (pd.to_datetime(to_date) - pd.to_datetime(from_date)).days + 1
#max_days1 = site_restr1.groupby(level=['site']).transform('sum')
#site_restr2 = (site_restr1/max_days1).round(3).unstack('restr_category')
##


## Combine cwms with lowflow sites

lowflow3 = pd.merge(sites2, lowflow2, on='site')

sites_zone_count = lowflow3[['site', 'cwms']].drop_duplicates().groupby('cwms').site.count()
sites_zone_count['All Canterbury'] = sites_zone_count.sum()

sites_zone_count_plot = ((sites_zone_count*0.1).apply(np.ceil) * 10).astype(int)

restr_all = lowflow3.groupby(['restr_category', 'flow_method', 'date'])[['site']].count()
restr_all['cwms'] = 'All Canterbury'
restr_all1 = restr_all.reset_index().set_index(['cwms', 'restr_category', 'flow_method', 'date']).site

restr1 = lowflow3.groupby(['cwms', 'restr_category', 'flow_method', 'date'])['site'].count()

restr2 = pd.concat([restr_all1, restr1])

restr2.name = 'Number of low flow sites on restriction'

restr2 = restr2.loc[:, ['Full', 'Partial']]

restr3 = restr2.unstack([0, 1, 2]).fillna(0)
#restr4 = restr3[['Full', 'Partial', 'No']]


###############################################3
### Iterate through zones

for zone in restr3.columns.levels[0]:
    if (zone not in restr3):
        restr4 = pd.DataFrame(np.repeat(0, len(restr3.index)), index=restr3.index, columns=['Full'])
        restr4.columns.name = 'restr_category'
    else:
        restr4 = restr3[zone].copy()
    y_max = sites_zone_count_plot.loc[zone]

    d1 = restr4.columns.to_frame()
    if 'Full' in d1.restr_category:
        full_n = len(d1.loc['Full'])
    else:
        full_n = 0
    if 'Partial' in d1.restr_category:
        partial_n = len(d1.loc['Partial'])
    else:
        partial_n = 0

    all_colors = []
    all_colors.extend(full_color[:full_n])
    all_colors.extend(partial_color[:partial_n])
    #all_colors.extend(no_color)

    ### Plots
    ## Set basic plot settings
    sns.set_style("white")
    sns.set_context('poster')

    fig, ax = plt.subplots(figsize=(15, 10))
    restr4.plot.area(stacked=True, ax=ax, color=all_colors)
    x_axis = ax.axes.get_xaxis()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], title='Restriction Categories', loc='upper left')
    ax.set_ylim(0, y_max)
    x_label = x_axis.get_label()
    x_label.set_visible(False)
    ax.yaxis.set_major_locator(loc)
    ax.set_ylabel('Number of low flow sites on restriction')
    y_axis = ax.axes.get_yaxis()
    xticks = ax.get_xticks()
    if len(xticks) > 15:
        for label in ax.get_xticklabels()[::2]:
            label.set_visible(False)
        ax.xaxis_date()
        fig.autofmt_xdate(ha='center')
    plt.title(zone)
    plt.tight_layout()

    plot2 = ax.get_figure()
    fancy_fig_name = '{from_date}_{to_date}_{zone}_lowflow_fancy.png'.format(from_date=from_date, to_date=to_date, zone=zone)

    plot2.savefig(path.join(export_path, fancy_fig_name))

    ### Non-fancy plot
    restr5 = restr4.sum(level=0, axis=1)

    ## Set basic plot settings
    sns.set_style("white")
    sns.set_context('poster')

    fig, ax = plt.subplots(figsize=(15, 10))
    restr5.plot.area(stacked=True, ax=ax, color=[full_color[3], partial_color[3]], ylim=[0, y_max], alpha=0.7)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], title='Restriction Categories', loc='upper left')
    x_axis = ax.axes.get_xaxis()
    x_label = x_axis.get_label()
    x_label.set_visible(False)
    ax.yaxis.set_major_locator(loc)
    ax.set_ylabel('Number of low flow sites on restriction')
    xticks = ax.get_xticks()
    if len(xticks) > 15:
        for label in ax.get_xticklabels()[::2]:
            label.set_visible(False)
        ax.xaxis_date()
        fig.autofmt_xdate(ha='center')
    plt.title(zone)
    plt.tight_layout()

    plot2 = ax.get_figure()

    norm_fig_name = '{from_date}_{to_date}_{zone}_lowflow_norm.png'.format(from_date=from_date, to_date=to_date, zone=zone)

    plot2.savefig(path.join(export_path, norm_fig_name))



### Manually calc sites
#man_calc_sites = lowflow1.loc[(lowflow1.date == to_date), ['site', 'waterway', 'location', 'flow_method']]
#man_calc_sites.to_csv(path.join(export_path, export_man_calc_sites), index=False)
#

#set2 = lowflow2[(lowflow2.date == '2017-10-01') & (lowflow2.restr_category != 'No')]
#set2.to_csv(path.join(export_path, export_sel2), index=False)
