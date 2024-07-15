import pandas as pd
import json
from pathlib import Path
from data_util import DataModel

#----------------------------------------------------------------
# Contains helper functions for the tranformation of geoJSON for map layers.
#----------------------------------------------------------------

class GeoJTransformer():
    
    # Loading data from the datamodel, as this needs to be joined with the geo data.
    dm = DataModel()
    dm_data = dm.get_data()
    
    def __init__(self) -> None:
        # get the polygon data for countries from github.
        json_path = Path(__file__).parent / "countries.geojson"
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
    def get_geo_data(self) -> pd.DataFrame:
        """
        Returning the dataframe stored in the data attribute.
        Returns:
            pd.DataFrame: DataFrame containg the polygon data for each country.
        """
        return self.data
    
    def get_choro_data(self) -> pd.DataFrame:
        """
        Merges two DataFrames, one with a full set of countries and their abbreviations, and another with a subset of countries and their cancer data.
        Returns:
            pd.DataFrame: Merged DataFrame with country information on cancer and country name/abbreviation.
        """
        
        # change json into dataframe and only keep the abbreviated Country name and the full country name.
        geo_sliced = pd.json_normalize(self.data["features"]).iloc[:, 1:3]
        
        # merge geo data and shaped data from datamodel, while keeping all the abbreviated country names.
        choro_data = pd.merge(left=geo_sliced, 
                              right=GeoJTransformer.dm_data, 
                              left_on="properties.name", 
                              right_on="country", 
                              how="left")
        
        # Fill everything that has no value due to the left-join.
        choro_data.fillna(0, inplace=True)
        
        return choro_data