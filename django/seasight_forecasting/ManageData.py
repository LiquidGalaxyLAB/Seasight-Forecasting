
import cdsapi
import datetime
import os
import shutil
import zipfile
import geopandas as gpd
import pandas as pd
import xarray as xr
from shapely.ops import cascaded_union
from seasight_forecasting import global_vars

def LoadData(data_path):    
    return pd.read_csv(data_path)

def GetDataFromAPI():
    data = ''
    tmpPath = 'tmp/'
    filePath = 'file/'

    os.mkdir(tmpPath)

    c = cdsapi.Client()
    c.retrieve(
        'satellite-sea-surface-temperature',
        {
            'processinglevel': 'level_4',
            'sensor_on_satellite': 'combined_product',
            'version': '2_0',
            'year': '2018',
            'month': '12',
            'day': '31',
            'variable': 'all',
            'format': 'zip',
        },
        tmpPath + 'download.zip')

    with zipfile.ZipFile(tmpPath + 'download.zip', 'r') as zip_ref:
        zip_ref.extractall(tmpPath + filePath)
    
    for filename in os.listdir(tmpPath + filePath):
        print('Downloaded file: {}'.format(filename))
        with xr.open_dataset(tmpPath + filePath + '/' + filename) as ds:
            ds = (ds.to_dataframe()).dropna()
            ds = ds.rename(columns={"analysed_sst": "sst"})
            ds = ds.drop(['analysis_uncertainty', 'sea_ice_fraction', 'mask'], axis=1).reset_index()
            ds['sst'] = ds['sst'].apply(lambda x: x - 273,15)
            ds['lat'] = ds['lat'].apply(lambda x: round(x * 2) / 2)
            ds['lon'] = ds['lon'].apply(lambda x: round(x * 2) / 2)
            data = ds.groupby(['time', 'lat', 'lon'])['sst'].mean().reset_index()
    
    shutil.rmtree(tmpPath, ignore_errors=True)
    print('Temporary files removed!')

    return data

def GetDataFromRegion(data, region):
    regions = {
        "North Atlantic Ocean": global_vars.north_atlantic_region_path,
        "South Atlantic Ocean": global_vars.south_atlantic_region_path,
        "Indian Ocean": global_vars.indian_region_path,
        "West Pacific Ocean": global_vars.west_pacific_region_path,
        "East Pacific Ocean": global_vars.east_pacific_region_path,
    }
    regionFile = gpd.read_file(regions[region])
    pol = cascaded_union(regionFile['geometry'])
    pol_gpd= gpd.GeoDataFrame()
    pol_gpd['geometry'] = None
    pol_gpd.loc[0,'geometry'] = pol
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lon, data.lat))
    data = gpd.sjoin(gdf, pol_gpd, op = 'within')
    data = data.drop(['geometry', 'index_right'], axis=1)
    return data

def GetDataInDateRange(data, dateFrom, check, dateTo):
    data = data[data.time > dateFrom]
    if check:
        data = data[data.time < str((datetime.datetime.strptime(dateTo, '%Y-%m-%d') + datetime.timedelta(days=1)))]
    return data