
import numpy as np
import osmnx as ox
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely import geometry
from shapely.ops import polygonize
import numpy as np
import pandas as pd
from tqdm import tqdm
from osm.osm_file_processor import OSMFileProcessor
import os


# Path: buildings/buildings_processor.py


class BuildingProcessor:
    """
    A class used to process building data from OpenStreetMap.

    Attributes:
        location (str): The location of the building.

    Methods:
        clean_buildings(buildings_gdf: GeoDataFrame) -> GeoDataFrame:
            Cleans the given GeoDataFrame of buildings by removing non-polygonal elements and unnecessary columns.
        retrieve_building_data() -> GeoDataFrame:
            Retrieves building data from OpenStreetMap within the bounding box defined by north, south, east, and west coordinates.
            Only buildings with the 'building' tag are included.
        insert_levels_to_buildings(buildings_gdf: GeoDataFrame) -> GeoDataFrame:
            Inserts levels to buildings based on the probability distribution of the number of levels.
        generate_height_probability(buildings_gdf: GeoDataFrame, is_raster_data=False) -> np.ndarray:
            Generates a probability distribution of building heights based on the input GeoDataFrame.
        convert_levels_to_height(buildings_gdf: GeoDataFrame) -> GeoDataFrame:
            Converts the number of levels of each building in the GeoDataFrame to its height in meters.
        process_buildings() -> GeoDataFrame:
            Processes building data from OpenStreetMap.
    """

    def __init__(self, location=None):
        """
        Initializes a new instance of the BuildingsProcessor class.

        Args:
            location (str, optional): The location of the building. Defaults to None.
        """
        self.location = location

    def clean_buildings(self, buildings_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Cleans the given GeoDataFrame of buildings by removing non-polygonal elements and unnecessary columns.

        Parameters:
        buildings_gdf (GeoDataFrame): A GeoDataFrame containing building data.

        Returns:
        GeoDataFrame: A cleaned GeoDataFrame containing only polygonal building elements and necessary columns.
        """
        print("Cleaning buildings...")
        buildings_gdf.reset_index(inplace=True)
        # # Remain only the relation element_type
        buildings_gdf = buildings_gdf[buildings_gdf["element_type"] != "point"]
        # Drop elements on the geometry columns that are not polygons
        buildings_gdf = buildings_gdf[buildings_gdf["geometry"].apply(
            lambda x: isinstance(x, geometry.Polygon) or isinstance(x, geometry.MultiPolygon))]
        # Remove the columns that we don't need
        columns_we_need = ["osmid", "building", "geometry", "building:levels"]
        # Replace all that contain a ',' with a nan value
        buildings_gdf['building:levels'].replace(
            r'.*,.*', np.nan, regex=True, inplace=True)
        buildings_gdf = buildings_gdf[columns_we_need]
        return buildings_gdf

    def retrieve_building_data(self, osm_file=None) -> GeoDataFrame:
        """
        Retrieves building data from OpenStreetMap within the bounding box defined by north, south, east, and west coordinates.
        Only buildings with the 'building' tag are included.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the retrieved building data.
        """
        print("Retrieving building data...")
        # Get the building data
        # Check if the osm_file is not None so we can use it instead of downloading the data
        if osm_file is not None:
        
            # Create an instance of the OSMFileProcessor class
            osm_file_processor = OSMFileProcessor(osm_file)
            
            # Process the OSM file and return a GeoDataFrame with the building data
            buildings_gdf = osm_file_processor.process_osm_file(type="buildings")

            buildings_gdf['element_type'] = 'relation'
            
            # Explode the multipolygons to create a polygon for each building
            gdf_exploded= buildings_gdf.explode()
            
            # Reset the index and drop the old index column
            buildings_gdf = gdf_exploded.reset_index(drop=True)

        else:
            buildings_gdf = ox.features.features_from_bbox(
                north=self.location["north"], south=self.location["south"], east=self.location["east"], west=self.location["west"], tags={'building': True})
        # Clean the buildings
        buildings_gdf = self.clean_buildings(buildings_gdf)
        return buildings_gdf

    def insert_levels_to_buildings(self, buildings_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Inserts levels to buildings based on the probability distribution of the number of levels.

        Args:
            buildings_gdf (GeoDataFrame): A GeoDataFrame containing the buildings data.

        Returns:
            GeoDataFrame: A GeoDataFrame with the updated buildings data.
        """
        print("Inserting levels to buildings...")
        # Make sure not NAN lanes are integers
        buildings_gdf["building:levels"] = buildings_gdf["building:levels"].fillna(
            -1).astype(int)
        # Iter rows of pandas dataframe and replace the 0 values with a random value based on the probability distribution of the number of levels
        n_levels_prob = self.generate_height_probability(
            buildings_gdf, is_raster_data=False)
        # Copy the dataframe
        buildings_gdf_copy = buildings_gdf.copy()
        # Drop the rows with nan values on the lane column
        buildings_gdf_copy = buildings_gdf_copy[buildings_gdf_copy['building:levels'] > 0]
        for index, row in tqdm(buildings_gdf.iterrows()):
            if row['building:levels'] < 0:
                buildings_gdf.loc[index, 'building:levels'] = np.random.choice(
                    buildings_gdf_copy['building:levels'], 1, p=n_levels_prob)

        return buildings_gdf

    @staticmethod
    def generate_height_probability(buildings_gdf: GeoDataFrame, is_raster_data=False) -> np.ndarray:
        """
        Generates a probability distribution of building heights based on the input GeoDataFrame.

        Args:
            buildings_gdf (GeoDataFrame): A GeoDataFrame containing building data.
            is_raster_data (bool, optional): A flag indicating whether the input data is raster data. Defaults to False.

        Returns:
            np.ndarray: An array of probabilities representing the distribution of building heights.
        """
        print("Generating height probability...")
        # Copy the dataframe
        buildings_gdf_copy = buildings_gdf.copy()
        if not is_raster_data:
            # Drop the rows with values < 0 on the height column
            buildings_gdf_copy = buildings_gdf_copy[buildings_gdf_copy['building:levels'] > 0]
            total_buildings = np.sum(buildings_gdf_copy['building:levels'])
            n_levels_prob = np.true_divide(
                buildings_gdf_copy['building:levels'], total_buildings)
            return n_levels_prob
        else:
            print("Generating height probability for raster data...")

    @staticmethod
    def convert_levels_to_height(buildings_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Converts the number of levels of each building in the GeoDataFrame to its height in meters.

        Args:
        buildings_gdf (GeoDataFrame): A GeoDataFrame containing the buildings to be processed.

        Returns:
        GeoDataFrame: A GeoDataFrame with the height of each building calculated and added as a new column.
        """
        print("Converting levels to height...")
        # Calculate the height of the buildings
        buildings_gdf["height"] = buildings_gdf["building:levels"] * 3
        buildings_gdf["height"] = buildings_gdf["height"].astype(int)
        # Replace all 0 height values with 3
        buildings_gdf["height"] = buildings_gdf["height"].replace(0, 3)
        return buildings_gdf
    
    def process_buildings(self, osm_file=None)-> GeoDataFrame:
        """
        Processes building data from OpenStreetMap.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the processed building data.
        """
        buildings_gdf = self.retrieve_building_data(osm_file=osm_file)
        buildings_gdf = self.insert_levels_to_buildings(buildings_gdf)
        buildings_gdf = self.convert_levels_to_height(buildings_gdf)
        return buildings_gdf

