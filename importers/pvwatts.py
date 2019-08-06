import os
import pandas as pd
import requests

API_KEY = os.environ['PVWATTS_API_KEY']

def load(system_capacity=4, module_type=0, losses=14, array_type=0, tilt=25, azimuth=180, address=None, lat=51.9607, lon=7.6261, radius=0):
    """
    Imports data from PVWatts using the requests package.
    Only fields that are of importance for this forecasting purpose
    can be specified.
    """
    params = {
        'api_key': API_KEY,
        'system_capacity': system_capacity,
        'module_type': module_type,
        'losses': losses,
        'array_type': array_type,
        'tilt': tilt,
        'azimuth': azimuth,
        'address': address,
        'lat': lat,
        'lon': lon,
        'radius': radius,
        'timeframe': 'hourly',
        'dataset': 'tmy3'
    }

    response = requests.get('https://developer.nrel.gov/api/pvwatts/v6.json', params)
    response.raise_for_status()
    outputs = response.json()['outputs']

    data = {key: outputs[key] for key in ['ac', 'tamb', 'wspd']}
    data['power'] = data.pop('ac')
    data = pd.DataFrame(data)
    data['time'] = pd.date_range('20190101', periods=len(data), freq='H')
    data.set_index('time', inplace=True)
    return data

def bulk_load_from_list(filepath, range=None):
    """
    Bulk Imports data from PVWatts using the load method.

    filepath: str. Path to a csv file containing the columns 'city', 'lat' and 'lon'
    range: tuple. range of cities to load
    """
    list = pd.read_csv(filepath)
    if not range: range = (0, len(list))
    start, stop = range
    list = list[start:stop]
    cities = {}
    for index, (city, lat, lon) in enumerate(list.values):
        cities[city] = load(lat=lat, lon=lon)
    return cities

def load_city_from_list(filepath, city):
    """
    Import a specific City

    filepath: str. Path to a csv file containing the columns 'city', 'lat' and 'lon'
    city: str. City name
    """
    list = pd.read_csv(filepath).set_index('city')
    city = list.loc[city]
    return load(lat=city.lat, lon=city.lon)
