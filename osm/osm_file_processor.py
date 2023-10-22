
import geopandas as gpd
from geopandas import GeoDataFrame
import os
import osmium
import shapely.wkb as wkblib
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
from tqdm import tqdm
from shapely.geometry import Point, LineString

# Path: osm/osm_file_processor.py


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
        elif type == 'highways':
            handler = HighwayHandler()
        else:
            raise Exception("Invalid type")
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

    def get_bounds_from_osm_file(self):
        """
        Get the bounds from the OSM file

        Returns:
            location (dict): The dict of the location bounds
        """
        location = {}
        try:
            box = osmium.io.Reader(self.osm_file).header().box()
            bottom_left = box.bottom_left
            top_right = box.top_right
            location['north'] = top_right.lat
            location['south'] = bottom_left.lat
            location['east'] = top_right.lon
            location['west'] = bottom_left.lon
            return location
        except Exception as e:
            print(f"An error occurred: {e}")


class BuildingHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.data = []
        self.wkbfab = osmium.geom.WKBFactory()

    def area(self, a):
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
        except Exception as e:
            print(f"An error occurred: {e}")


class HighwayHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.wkbfab = osmium.geom.WKBFactory()
        self.highways = []

    def way(self, w):
        if w.tags.get("highway") is not None and w.tags.get("name") is not None:
            try:
                points = []
                for node in w.nodes:
                    print(w.id, w.nodes)
                    try:
                        if node.lat is not None:
                            n = Point(node.location.lon, node.location.lat)
                            points.append(n)
                    except Exception as e:
                        print('\nSkipping node: {} (x={}, y={}) because of error: {}\n'.format(node.ref, node.location.lat_without_check(), node.location.lon_without_check(), e))
    
                geometry = LineString(points).wkt
                
                lanes = w.tags.get("lanes", None)
                highway = w.tags.get("highway", None)
                self.highways.append({
                    "osmid": w.id,
                    "geometry": geometry,
                    "lanes": lanes,
                    "highway": highway
                })
            except Exception as e:
                print(f"An error occurred: {e}")
