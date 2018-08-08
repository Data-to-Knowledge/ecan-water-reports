# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 13:07:42 2018

@author: MichaelEK
"""
import pandas as pd
import geopandas as gpd


def grp_ts_agg(df, grp_col, ts_col, freq_code):
    """
    Simple function to aggregate time series with dataframes with a single column of sites and a column of times.

    Parameters
    ----------
    df : DataFrame
        Dataframe with a datetime column.
    grp_col : str or list of str
        Column name that contains the sites.
    ts_col : str
        The column name of the datetime column.
    freq_code : str
        The pandas frequency code for the aggregation (e.g. 'M', 'A-JUN').

    Returns
    -------
    Pandas resample object
    """

    df1 = df.copy()
    if type(df[ts_col].iloc[0]) is pd.Timestamp:
        df1.set_index(ts_col, inplace=True)
        if type(grp_col) is list:
            grp_col.extend([pd.Grouper(freq=freq_code)])
        else:
            grp_col = [grp_col, pd.Grouper(freq=freq_code)]
        df_grp = df1.groupby(grp_col)
        return (df_grp)
    else:
        print('Make one column a timeseries!')


def multipoly_to_poly(geodataframe):
    """
    Function to convert a GeoDataFrame with some MultiPolygons to only polygons. Creates additional rows in the GeoDataFrame.

    Parameters
    ----------
    geodataframe: GeoDataFrame

    Returns
    -------
    GeoDataFrame
    """
    gpd1 = geodataframe.copy()
    gpd2 = gpd.GeoDataFrame()
    for i in gpd1.index:
        geom1 = gpd1.loc[[i]]
        geom2 = geom1.loc[i, 'geometry']
        if geom2.type == 'MultiPolygon':
            polys = [j for j in geom2]
            new1 = geom1.loc[[i] * len(polys)]
            new1.loc[:, 'geometry'] = polys
        else:
            new1 = geom1.copy()
        gpd2 = pd.concat([gpd2, new1])
    return gpd2.reset_index(drop=True)