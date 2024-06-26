#!/usr/bin/env python
import argparse
from main import main


def run_cli():

    parser = argparse.ArgumentParser(
        description="A tool to simplify the workflow of estimating pollutant concentrations in urban areas by automating the simulation process in GRAL .",
        epilog="""
        Examples:
        Run the entire process with the default configuration file:
        python cli.py -c configuration.sumo2gral.cfg --process all
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--base-directory", required=False,
                        help="The base directory for the project.", dest="base_directory")
    parser.add_argument("--north", type=float,
                        help="The northernmost latitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="north", default=None)
    parser.add_argument("--south", type=float,
                        help="The southernmost latitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="south", default=None)
    parser.add_argument("--east", type=float,
                        help="The easternmost longitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="east", default=None)
    parser.add_argument("--west", type=float,
                        help="The westernmost longitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="west", default=None)
    parser.add_argument("--epsg", type=int,
                        help="The EPSG code for the coordinate system to reproject the map to, ie: 3857.", default=3857, dest="epsg")
    parser.add_argument("--process", choices=["all", "map", "buildings", "weather", "highways", "gral", "results", "vegetation"],
                        help="Specify the process to run. Choices are: all, map, buildings, weather, highway, gral", required=True,  dest="process")
    parser.add_argument("--map-name", type=str, default="basemap",
                        help="The name of the map file to be saved.", dest="map_filename")
    parser.add_argument("--buildings-shp-file", type=str, default="buildings.shp",
                        help="The name of the shapefile to be saved.", dest="buildings_shapefile_filename")
    parser.add_argument("--highways-shp-file", type=str, default="highways.shp", help="The name of the shapefile to be saved.",
                        dest="highways_shapefile_filename")
    parser.add_argument("--vegetation-shp-file", type=str, default="vegetation.shp", help="The name of the shapefile to be saved.",
                        dest="vegetation_shapefile_filename")
    parser.add_argument("--net-file", type=str, required=False, default="net.net.xml", help="The name of the SUMO network file.",
                        dest="net_file")
    parser.add_argument("--emissions-file", type=str, required=False , default="emissions.xml",
                        help="The name of the SUMO emissions file.", dest="emissions_file")
    parser.add_argument("--weather-file", type=str,
                        help="The name of the weather data file.", dest="weather_file")
    parser.add_argument("--output-weather-file", type=str, default="output_weather_data",
                        help="The name of the output weather data file.", dest="output_weather_file")
    parser.add_argument("--weather-day", type=str,
                        help="The day of the weather data to extract, format (dd.mm.yyyy)", dest="weather_day", default=None)
    parser.add_argument("--weather-hour", type=str,
                        help="The hour of the weather data to extract, format (hh:mm)", dest="weather_hour", default=None)
    parser.add_argument("--met-file", type=str, default="weather.met", help="The name of the met file.",
                        dest="met_file")
    parser.add_argument("--gral-dll", type=str,required=False,
                        help="The name of the GRAL executable.", dest="gral_dll")
    parser.add_argument("--osm-file", type=str, default=None,
                        help="The name of the OSM file.", dest="osm_file")
    parser.add_argument("--pollutant", type=str, default="NOx",
                        help="The pollutant to be simulated.", dest="pollutant")
    parser.add_argument("--hor-layers", type=list, default=[3, 6, 9],
                        help="The horizontal layers to be simulated (m.).", dest="hor_layers")
    parser.add_argument("--particles-ps", type=int, default=100, help="The number of particles per second.", dest="particles_ps")
    parser.add_argument("--dispertion-time", type=int, default=3600, help="The dispertion time (s.).", dest="dispertion_time")
    parser.add_argument("--n-cores", type=int, default=4, help="The number of cores of CPU used for the simulation", dest="n_cores")
    parser.add_argument("--online", default=False, action="store_true",
                        help="The program by default executes the offline mode. If you dont provide any osm or net files it is recommended to use online", dest="is_online")
    parser.add_argument("-c", "--config" ,default=False, help="Use the configuration file", dest="config")
    parser.add_argument("--display-geo-map", default=False, action="store_true", help="Display the results on a geopgrahic map", dest="display_geo_map")
    parser.add_argument("-r", "--results", default=False, help="The name of the results file", dest="results")
    parser.add_argument("--mapbox-api-key", default=None, help="The mapbox api key", dest="mapbox_api_key")
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    run_cli()
