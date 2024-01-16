
import geopandas as gpd
import os
import osmium
import shapely.wkb as wkblib
import pandas as pd
from tqdm import tqdm
import sumolib as sumo
from shapely.geometry import Point, LineString
import warnings
import xml.etree.ElementTree as ET

# Path: local_files_processor/local_file_processor.py


class OSMFileProcessor:

    def __init__(self, osm_file):
        """
        Initialize the OSMFileProcessor class

        Args:
            osm_file (str): The path to the OSM file
        """

        self.osm_file = osm_file

    def remove_temp_files(self, temp_files: list) -> None:
        """
        Remove the temp files created during the process

        Args:
            temp_files (list): The list of the temp files

        Returns:
            None
        """
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def process_osm_file(self, type=None):
        """
        Process the OSM file and return a GeoDataFrame

        Args:
            type (str): The type of the OSM file to process

        Returns:
            gdf (GeoDataFrame): The GeoDataFrame of the OSM file
        """
        if type == 'buildings':
            handler = BuildingHandler()
        else:
            raise Exception(f"Invalid type. The type must be buildings, and is {type}")
        handler.apply_file(self.osm_file)
        df = pd.DataFrame(handler.data)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
        return gdf

    def convert_osm_to_pbf_file(self, pbf_file):
        """
        Convert the OSM file to a PBF file using osmium tool

        Args:
            pbf_file (str): The path to the PBF file

        Returns:
            None
        """
        os.system(f"osmium cat -o {pbf_file} {self.osm_file}")


class BuildingHandler(osmium.SimpleHandler):

    def __init__(self):
        """
        Initialize the BuildingHandler class
        """
        osmium.SimpleHandler.__init__(self)
        self.data = []
        self.wkbfab = osmium.geom.WKBFactory()

    def area(self, a):
        """
        Get the area of the building

        Args:
            a (osmium.osm.Area): The OSM area object

        Returns:
            None
        """
        try:
            if 'building' in a.tags:
                wkbshape = self.wkbfab.create_multipolygon(a)
                shapely_geom = wkblib.loads(wkbshape, hex=True)
                building_levels = a.tags.get('building:levels', None)
                building = a.tags.get('building', None)
                self.data.append({
                    'geometry': shapely_geom,
                    'building': building,
                    'building:levels': building_levels,
                    'element_type': 'area',
                    'osmid': a.id
                })
        except RuntimeError as e:
            warnings.warn(f"Warning {e}")


class NetFileProcessor:

    def __init__(self, sumo_net):
        """
        Initialize the NetFileProcessor class

        Args:
            sumo_net (sumolib.net.Net): A sumolib net object containing the SUMO network.
        """

        self.sumo_net = sumo_net

    def process_net_file(self):
        """
        Process the SUMO network file and return a GeoDataFrame

        Returns:
            edges_gdf (GeoDataFrame): The GeoDataFrame of the SUMO network
        """
        edges = self.sumo_net.getEdges()
        edges_id, edges_geometry = self.process_edges(edges)
        edges_gdf = gpd.GeoDataFrame({'edge_id': edges_id, 'geometry': edges_geometry},geometry='geometry', crs='EPSG:4326')
        return edges_gdf
    
    def process_edges(self, edges):
        """
        Process the edges of the SUMO network

        Args:
            edges (list): A list of sumolib.net.Edge objects

        Returns:
            edges_id (list): A list of the edge IDs
            edges_geometry (list): A list of the edge geometries
        """
        edges_id = []
        edges_geometry = []
        for edge in tqdm(edges):
            edge_shape = list(edge.getRawShape())
            if len(edge_shape) < 2:
                continue
            geometry = self.process_shapes(edge_shape)
            edges_id.append(edge.getID())
            edges_geometry.append(geometry)
        
        return edges_id, edges_geometry

    
    def process_shapes(self, edge_shapes):
        """
        Process the shapes of the edges of the SUMO network

        Args:
            edge_shapes (list): A list of the edge shapes
        
        Returns:
            geometry (LineString): The geometry of the edge
        """
        points = []
        for shape in edge_shapes:
            x, y = shape
            lon, lat = self.sumo_net.convertXY2LonLat(x, y)
            points.append(Point(lon, lat))
        geometry = LineString(points)
        return geometry
    
    def get_bounds_from_net_file(self):
        """
        Get the bounds from the net file

        Returns:
            location (dict): The dict of the location bounds
        """
        location = {}
       
        xmin,ymin,xmax,ymax = self.sumo_net.getBoundary()
        west, south = self.sumo_net.convertXY2LonLat(xmin, ymin)
        east, north = self.sumo_net.convertXY2LonLat(xmax, ymax)
        location['north'] = north
        location['south'] = south
        location['east'] = east
        location['west'] = west
        return location
        
    
class XMLFileProcessor():
    """
    Class to process the XML file

    Attributes:
        xml_file (str): The path to the XML file

    Methods:
        get_root: Process the XML file and return a DataFrame
        get_input_from_xml: Get the input values from the XML file
        get_output_from_xml: Get the output values from the XML file
        get_gral_from_xml: Get the GRAL value froms the XML file
    """

    def __init__(self, xml_file):
        """
        Initialize the XMLFileProcessor class

        Args:
            xml_file (str): The path to the XML file
        """

        self.xml_file = xml_file

    def get_root(self):
        """
        Process the XML file and return a DataFrame

        Returns:
            df (DataFrame): The DataFrame of the XML file
        """
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        return root

    def get_input_from_xml(root_element):
        
        """
        Get the input values from the XML file

        Args:
            root_element (Element): The root element of the XML file

        Returns:
            base_directory (str): The base directory for the project
            net_file (str): The path to the SUMO network file
            osm_file (str): The path to the OSM file
            emissions_file (str): The path to the SUMO emissions file
            met_file (str): The path to the met file
            gral_dll (str): The path to the GRAL executable
        """

        input_elem = root_element.find('input')
        base_directory = input_elem.find('base-directory').attrib['value']
        net_file = input_elem.find('net-file').attrib['value']
        osm_file = input_elem.find('osm-file').attrib['value']
        emissions_file = input_elem.find('emissions-file').attrib['value']
        met_file = input_elem.find('met-file').attrib['value']
        gral_dll = input_elem.find('gral-dll').attrib['value']
        return base_directory, net_file, osm_file, emissions_file, met_file, gral_dll

    def get_output_from_xml(root_element):
        """
        Get the output values from the XML file

        Args:
            root_element (Element): The root element of the XML file
        
        Returns:
            buildings_shp_file (str): The path to the buildings shapefile
            highways_shp_file (str): The path to the highways shapefile
        """
        output_elem = root_element.find('output')
        buildings_shp_file = output_elem.find('buildings-shp-file').attrib['value']
        highways_shp_file = output_elem.find('highways-shp-file').attrib['value']
        return buildings_shp_file, highways_shp_file

    def get_gral_from_xml(root_element):
        """
        Get the GRAL values from the XML file

        Args:
            root_element (Element): The root element of the XML file
        
        Returns:
            pollutant (str): The pollutant to be simulated
            hor_layers (list): The list of the horizontal layers
            particles_ps (int): The number of particles per second
            dispertion_time (int): The dispertion time
        """
        gral_elem = root_element.find('gral')
        pollutant = str(gral_elem.find('pollutant').attrib['value'])
        hor_layers = list(gral_elem.find('hor-layers').attrib['value'])
        particles_ps =int(gral_elem.find('particles-ps').attrib['value'])
        dispertion_time = int(gral_elem.find('dispertion-time').attrib['value'])
        return pollutant, hor_layers, particles_ps, dispertion_time