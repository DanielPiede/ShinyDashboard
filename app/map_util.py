import pandas as pd
import json
import urllib
from data_util import DataModel

class GeoJTransformer():
    
    dm = DataModel()
    dm_data = dm.get_data()
    
    def __init__(self):
        with urllib.request.urlopen("https://raw.githubusercontent.com/DanielPiede/ShinyDashboard/main/raw/countries.geojson") as url:
            self.data = json.load(url)
        
    def get_geo_data(self):
        return self.data
    
    def get_choro_data(self):
        
        # change json into dataframe and only keep the abbreviated Country name and the full country name.
        geo_sliced = pd.json_normalize(self.data["features"]).iloc[:, 1:3]
        
        # merge geo data and shaped data from datamodel, while keeping all the abbreviated country names.
        choro_data = pd.merge(left=geo_sliced, 
                              right=GeoJTransformer.dm_data, 
                              left_on="properties.name", 
                              right_on="country", 
                              how="left")
        
        # Fill everything that has no value due to the join.
        choro_data.fillna(0, inplace=True)
        
        return choro_data