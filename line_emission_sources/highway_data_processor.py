import osmnx as ox
import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
import sumolib as sumo
from tqdm import tqdm
import os
from osm.osm_file_processor import OSMFileProcessor



class HighwayDataProcessor:
    """
    A class used to process highway data from OpenStreetMap.

    Attributes:
        location (str): The location of the line emission sources.

    Methods:
        retrieve_highway_data(): Retrieves highway data from OpenStreetMap within a specified bounding box.
        clean_highway(highway_gdf: GeoDataFrame) -> GeoDataFrame: Cleans a GeoDataFrame containing highway data by removing all rows that are not of type "way", dropping unnecessary columns, and converting the "osmid" column to a string.
        generate_lanes_probability(highway_gdf: GeoDataFrame) -> np.ndarray: Generates the probability of each lane in a highway based on the number of lanes.
        insert_lanes_to_highway(highway_gdf: pd.DataFrame, sumo_net) -> pd.DataFrame: Inserts lanes to a highway GeoDataFrame by replacing 0 values with a random value based on the probability distribution of the number of lanes.
        calculate_width_of_highway(highway_gdf: GeoDataFrame) -> GeoDataFrame: Calculates the width of a highway based on the number of lanes.
    """
    
    def __init__(self, location):
        """
        Initializes a HighwayDataProcessor object with the given location.

        Args:
            location (str): The location of the line emission sources.

        Returns:
            None
        """
        self.location = location

    def retrieve_highway_data(self, osm_file=None):
        """
        Retrieves highway data from OpenStreetMap within a specified bounding box.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the highway data within the specified bounding box.
        """
        print("Retrieving highway data...")
        if osm_file is not None:

            # Create an instance of the OSMFileProcessor class
            osm_file_processor = OSMFileProcessor(osm_file)

            # Process the OSM file and return a GeoDataFrame with the building data
            highways_gdf = osm_file_processor.process_osm_file(type="highways")

            # Add the element type column
            highways_gdf['element_type'] = 'way'

        else:
            # Get the highway data
            highways_gdf = ox.features.features_from_bbox(
                north=self.location["north"],
                south=self.location["south"],
                east=self.location["east"],
                west=self.location["west"],
                tags={'highway': True}
            )

        # Clean the highways
        highways_gdf = self.clean_highway(highways_gdf)
        print(highways_gdf)
        return
        return highways_gdf

    @staticmethod
    def clean_highway(highway_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Cleans a GeoDataFrame containing highway data by removing all rows that are not of type "way",
        dropping unnecessary columns, and converting the "osmid" column to a string.

        Args:
            highway_gdf (GeoDataFrame): A GeoDataFrame containing highway data.

        Returns:
            GeoDataFrame: A cleaned GeoDataFrame containing only "way" rows, necessary columns, and a string "osmid" column.
        """
        print("Cleaning highway...")
        highway_gdf.reset_index(inplace=True)
        # Remain only the way element_type
        highway_gdf = highway_gdf[highway_gdf["element_type"] == "way"]
        # Remove the columns that we don't need
        columns_we_need = ["osmid", "highway", "geometry", "lanes"]
        highway_gdf = highway_gdf[columns_we_need]
        # Convert the osmid to string
        highway_gdf["osmid"] = highway_gdf["osmid"].astype(str)
        return highway_gdf

    @staticmethod
    def generate_lanes_probability(highway_gdf: GeoDataFrame) -> np.ndarray:
        """
        Generate the probability of each lane in a highway based on the number of lanes.

        Parameters:
        highway_gdf (gpd.GeoDataFrame): A GeoDataFrame containing the highway data.

        Returns:
        np.ndarray: An array containing the probability of each lane.
        """
        print("Generating lanes probability...")
        # Copy the dataframe
        highway_df_copy = highway_gdf.copy()
        # Drop the rows with 0 values on the lane column
        highway_df_copy = highway_df_copy[highway_df_copy['lanes'] > 0]
        total_ways = np.sum(highway_df_copy['lanes'])
        n_lanes_prob = np.true_divide(highway_df_copy['lanes'], total_ways)
        return n_lanes_prob

    def insert_lanes_to_highway(self, highway_gdf: pd.DataFrame, sumo_net) -> pd.DataFrame:
        """
        Inserts lanes to a highway GeoDataFrame by replacing 0 values with a random value based on the probability
        distribution of the number of lanes.

        Args:
            highway_gdf (pd.DataFrame): A GeoDataFrame containing the highway data.
            sumo_net (sumolib.net.Net): A sumolib net object containing the SUMO network.

        Returns:
            pd.DataFrame: A GeoDataFrame with the updated number of lanes.
        """
        print("Inserting lanes to highway...")
        # Make sure not NAN lanes are integers
        highway_gdf["lanes"] = highway_gdf["lanes"].fillna(0).astype(int)
        # Iterate over the rows and assign a number of lanes based on the sumo network
        print("Assigning number of lanes based on the sumo network...")
        for index, row in tqdm(highway_gdf.iterrows()):
            original_id = row['osmid']
            edges = sumo_net.getEdgesByOrigID(original_id)
            if len(edges) > 0:
                for edge in edges:
                    n_lanes = edge.getLaneNumber()
                    highway_gdf.loc[index, 'lanes'] = n_lanes

        n_lanes_prob = self.generate_lanes_probability(highway_gdf)
        # Copy the dataframe
        highway_gdf_copy = highway_gdf.copy()
        # Drop the rows with nan values on the lane column
        highway_gdf_copy = highway_gdf_copy[highway_gdf_copy['lanes'] > 0]
        # Iter rows of pandas dataframe and replace the 0 values with a random value based on the probability
        print("Assigning number of lanes based on the probability distribution...")
        for index, row in tqdm(highway_gdf.iterrows()):
            if row['lanes'] <= 0:
                highway_gdf.loc[index, 'lanes'] = np.random.choice(
                    highway_gdf_copy['lanes'], 1, p=n_lanes_prob)

        return highway_gdf

    @staticmethod
    def calculate_width_of_highway(highway_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Calculates the width of a highway based on the number of lanes.

        Args:
            highway_gdf (GeoDataFrame): A GeoDataFrame containing the highway data.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the highway data with an additional "width" column.
        """
        print("Calculating width of highway...")
        # Calculate the width of the highway
        highway_gdf["width"] = highway_gdf["lanes"] * 3
        highway_gdf["width"] = highway_gdf["width"].astype(int)
        return highway_gdf

    def process_highway_data(self, sumo_net, osm_file=None):
        """
        Processes highway data by retrieving the highway data, inserting lanes to the highway, calculating the width of the highway,

        Args:
            sumo_net (sumolib.net.Net): A sumolib net object containing the SUMO network.
            osm_file (str, optional): The path to the OSM file. Defaults to None.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the processed highway data.
        """
        highway_gdf = self.retrieve_highway_data(osm_file)
        highway_gdf = self.insert_lanes_to_highway(highway_gdf, sumo_net)
        highway_gdf = self.calculate_width_of_highway(highway_gdf)
        highway_gdf = self.add_emission_src_group(highway_gdf)
        return highway_gdf

    def process_sumo_edges_emissions_file(self, filename, sumo_net, osm_id_list):
        """
        Reads a SUMO emissions file and returns a pandas DataFrame with the aggregated emissions per OSM ID.

        Args:
            filename (str): The path to the SUMO emissions file.
            sumo_net (sumolib.net.Net): A sumolib net object containing the SUMO network.
            osm_id_list (list): A list of osm ids.

        Returns:
            pandas.DataFrame: A DataFrame with the aggregated emissions per OSM ID, with columns 'osmid', 'edge_NOx_normed',
            and 'edge_PMx_normed'.
        """
        print("Reading sumo emissions file...")
        sumo_emissions_df = pd.read_csv(filename, delimiter=";")
        # Convert edges to osm id
        sumo_emissions_df = self.convert_sumo_edges_to_osm_id(
            sumo_emissions_df, sumo_net, osm_id_list)
        sumo_emissions_df = sumo_emissions_df.groupby('osmid').agg(
            {'edge_NOx_normed': 'sum', 'edge_PMx_normed': 'sum'})
        sumo_emissions_df.reset_index(inplace=True)

        return sumo_emissions_df

    @staticmethod
    def convert_sumo_edges_to_osm_id(edges_emissions_df: pd.DataFrame, sumo_net: sumo.net.Net, osm_id_list: list) -> pd.DataFrame:
        """
        Converts the edges of the sumo emission edges file to osm id.

        Args:
        edges_emissions_df (pandas.DataFrame): A pandas dataframe containing the sumo emission edges file.
        sumo_net (sumolib.net.Net): A sumolib net object containing the SUMO network.
        osm_id_list (list): A list of osm ids.

        Returns:
        pandas.DataFrame: A pandas dataframe containing the sumo emission edges file with an additional column 'osmid' 
        that contains the osm id of each edge.
        """
        print("Converting the edges of the sumo emission edges file to osm id...")
        # Explicitly create the 'osmid' column with type 'object' (string)
        edges_emissions_df['osmid'] = np.nan
        edges_emissions_df['osmid'] = edges_emissions_df['osmid'].astype(
            object)

        # Create a dictionary with the osm id and the edge id as the value. Lambda function to get the osm id from the edge id
        osm_id_edge_id_dict = {osm_id: sumo_net.getEdgesByOrigID(
            osm_id) for osm_id in osm_id_list}

        # Cast all edge ID values that are not strings to strings
        edges_emissions_df['edge_id'] = edges_emissions_df['edge_id'].astype(
            str)
        # Iterate over the dictionary and get the osm id
        for osm_id, edges_set in tqdm(osm_id_edge_id_dict.items()):
            if len(edges_set) > 0:
                for edge in edges_set:
                    edge_id = edge.getID()
                    # Cast all edge ID values that are not strings to strings
                    if type(edge.getID()) != str:
                        edge_id = str(edge.getID())
                    # Insert the osm id in the dataframe based on the edge id
                    edges_emissions_df.loc[(
                        (edges_emissions_df['edge_id'] == edge_id)), 'osmid'] = osm_id

        return edges_emissions_df

    def combine_sumo_emissions_and_highway_data(self, sumo_emissions_df: pd.DataFrame, highway_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Combines SUMO emissions and highway data by merging the dataframes on the 'osmid' column, 
        joining rows with the same 'osmid', and cleaning the resulting dataframe. 

        Args:
        sumo_emissions_df (pandas.DataFrame): SUMO emissions dataframe.
        highway_gdf (geopandas.GeoDataFrame): Highway geodataframe.

        Returns:
        pandas.GeoDataFrame: Combined and cleaned SUMO emissions and highway data.
        """
        print("Combining sumo emissions and highway data...")
        # Merge the sumo emissions and highway
        sumo_emissions_highway_df = pd.merge(
            sumo_emissions_df, highway_gdf, on="osmid", how="outer")
        # Join rows with the same osmid
        sumo_emissions_highway_df = sumo_emissions_highway_df.groupby("osmid").agg(
            {"edge_NOx_normed": "sum", "edge_PMx_normed": "sum", "highway": "first", "geometry": "first", "lanes": "first", "width": "first"})
        # Clean the sumo emissions and highway data
        sumo_emissions_highway_df = self.clean_sumo_emisisons_highway_data(
            sumo_emissions_highway_df)

        # Convert DataFrame to GeoDataFrame
        sumo_emissions_highway_gdf = GeoDataFrame(
            sumo_emissions_highway_df, geometry="geometry", crs="EPSG:4326")
        return sumo_emissions_highway_gdf

    @staticmethod
    def clean_sumo_emisisons_highway_data(sumo_emissions_highway_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the given SUMO emissions and highway data by dropping rows with NaN values on the geometry column,
        and dropping rows with pedestrian, cycleway, and footway on the highway column. Resets the index of the resulting
        dataframe.

        Args:
            sumo_emissions_highway_df (pandas.DataFrame): The SUMO emissions and highway data to be cleaned.

        Returns:
            pandas.DataFrame: The cleaned SUMO emissions and highway data.
        """
        print("Cleaning sumo emissions and highway data...")
        # Drop the rows with nan values on the geometry column
        sumo_emissions_highway_df = sumo_emissions_highway_df[sumo_emissions_highway_df["geometry"].notna(
        )]
        # Drop the rows with pedestrian, cycleway, and footway on the highway column
        sumo_emissions_highway_df = sumo_emissions_highway_df[
            sumo_emissions_highway_df["highway"] != "cycleway"]
        sumo_emissions_highway_df = sumo_emissions_highway_df[
            sumo_emissions_highway_df["highway"] != "footway"]
        # Reset the index
        sumo_emissions_highway_df.reset_index(inplace=True)

        return sumo_emissions_highway_df

    @staticmethod
    def add_emission_src_group(highways_gdf: GeoDataFrame) -> GeoDataFrame:
        """
        Adds an 'emission_src_group' column to the input dataframe and sets its value to 'highway'.

        Args:
            highways_df (pandas.DataFrame): The input dataframe to which the 'emission_src_group' column will be added.

        Returns:
            pandas.GeoDataframe: The input dataframe with the 'emission_src_group' column added and its value set to 'highway'.
        """
        print("Adding emission src group...")
        # Add the emission src group
        highways_gdf["emission_src_group"] = "highway"
        return highways_gdf
