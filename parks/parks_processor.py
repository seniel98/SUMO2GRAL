import numpy as np
import osmnx as ox
from geopandas import GeoDataFrame
from shapely import geometry
import numpy as np
from tqdm import tqdm
from local_files_processor.local_file_processor import OSMFileProcessor


# Path: parks/parks_processor.py


class ParksProcessor:
    """
    A class used to process park data from OpenStreetMap.

    Attributes:
        location (str): The location of the park.

    Methods:
        clean_parks(parks_gdf: GeoDataFrame) -> GeoDataFrame:
            Cleans the given GeoDataFrame of parks by removing non-polygonal elements and unnecessary columns.
        retrieve_park_data() -> GeoDataFrame:
            Retrieves park data from OpenStreetMap within the bounding box defined by north, south, east, and west coordinates.
            Only parks with the 'park' tag are included.
        insert_levels_to_parks(parks_gdf: GeoDataFrame) -> GeoDataFrame:
            Inserts levels to parks based on the probability distribution of the number of levels.
        generate_height_probability(parks_gdf: GeoDataFrame, is_raster_data=False) -> np.ndarray:
            Generates a probability distribution of park heights based on the input GeoDataFrame.
        convert_levels_to_height(parks_gdf: GeoDataFrame) -> GeoDataFrame:
            Converts the number of levels of each park in the GeoDataFrame to its height in meters.
        process_parks() -> GeoDataFrame:
            Processes park data from OpenStreetMap.
    """

    def __init__(self, location=None):
        """
        Initializes a new instance of the ParksProcessor class.

        Args:
            location (str, optional): The location of the park. Defaults to None.
        """
        self.location = location

    def clean_parks(self, parks_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Cleans the given GeoDataFrame of parks by removing non-polygonal elements and unnecessary columns.

        Parameters:
        parks_gdf (GeoDataFrame): A GeoDataFrame containing park data.

        Returns:
        GeoDataFrame: A cleaned GeoDataFrame containing only polygonal park elements and necessary columns.
        """
        print("Cleaning parks...")
        parks_gdf.reset_index(inplace=True)
        # # Remain only the relation element_type
        parks_gdf = parks_gdf[parks_gdf["element_type"] != "point"]
        # Drop elements on the geometry columns that are not polygons
        parks_gdf = parks_gdf[parks_gdf["geometry"].apply(
            lambda x: isinstance(x, geometry.Polygon) or isinstance(x, geometry.MultiPolygon))]
        # Remove the columns that we don't need
        columns_we_need = ["osmid", "name", "geometry"]
        # Replace all that contain a ',' with a nan value
        parks_gdf = parks_gdf[columns_we_need]
        return parks_gdf

    def retrieve_park_data(self, is_online=False, osm_file=None) -> GeoDataFrame:
        """
        Retrieves park data from OpenStreetMap within the bounding box defined by north, south, east, and west coordinates.
        Only parks with the 'park' tag are included.

        Args:
            is_online (bool): The process to run. Tells whether the process is offline (False) or online (True) .
            osm_file (str, optional): The name of the OSM file. Defaults to None.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the retrieved park data.
        """
        print("Retrieving park data...")
        # Get the park data
        # Check if the osm_file is not None so we can use it instead of downloading the data
        if not is_online and osm_file is not None:
            print("Processing offline...")
            
            # Create an instance of the OSMFileProcessor class
            osm_file_processor = OSMFileProcessor(osm_file)
            
            # Process the OSM file and return a GeoDataFrame with the park data
            parks_gdf = osm_file_processor.process_osm_file(type="parks")

            parks_gdf['element_type'] = 'relation'
            
            # Explode the multipolygons to create a polygon for each park
            gdf_exploded= parks_gdf.explode()
            
            # Reset the index and drop the old index column
            parks_gdf = gdf_exploded.reset_index(drop=True)

        else:
            parks_gdf = ox.features.features_from_bbox(
                north=self.location["north"], south=self.location["south"], east=self.location["east"], west=self.location["west"], tags={'leisure:park': True})
        # Clean the parks
        parks_gdf = self.clean_parks(parks_gdf)
        return parks_gdf
    
    def process_parks(self, process="" ,osm_file=None)-> GeoDataFrame:
        """
        Processes parks data from OpenStreetMap.

        Args:
            process (str): The process to run. Can be 'offline'. Defaults to "".
            osm_file (str, optional): The name of the OSM file. Defaults to None.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the processed parks data.
        """
        parks_gdf = self.retrieve_park_data(process, osm_file=osm_file)
        return parks_gdf

