import argparse
from main import main


def run_cli():
    try:
        parser = argparse.ArgumentParser(
            description="A tool to automate the process of retrieving necessary inputs for the GRAL program.",
            epilog="""
    Examples:
    Retrieve only the map:
        python CLI.py --base_directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --epsg 3857 --process map
            """,
            formatter_class=argparse.RawTextHelpFormatter
        )

        parser.add_argument("--base_directory", required=True,
                            help="The base directory for the project.", dest="base_directory")
        parser.add_argument("--north", type=float,
                            help="The northernmost latitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="north")
        parser.add_argument("--south", type=float,
                            help="The southernmost latitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="south")
        parser.add_argument("--east", type=float,
                            help="The easternmost longitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="east")
        parser.add_argument("--west", type=float,
                            help="The westernmost longitude of the bounding box. Must be in EPSG:4326, and decimal degrees.", required=False, dest="west")
        parser.add_argument("--epsg", type=int,
                            help="The EPSG code for the coordinate system to reproject the map to, ie: 3857.", default=3857, dest="epsg")
        parser.add_argument("--process", choices=["all", "map", "buildings", "weather", "highways", "gral"],
                            help="Specify the process to run. Choices are: map, buildings, weather, highway, gral", required=True,  dest="process")
        parser.add_argument("--map_name", type=str, default="basemap",
                            help="The name of the map file to be saved.", dest="map_filename")
        parser.add_argument("--buildings_shp_file", type=str, default="buildings",
                            help="The name of the shapefile to be saved.", dest="buildings_shapefile_filename")
        parser.add_argument("--highways_shp_file", type=str, default="highways", help="The name of the shapefile to be saved.",
                            dest="highways_shapefile_filename")
        parser.add_argument("--net_file", type=str, default="net.net.xml", help="The name of the SUMO network file.",
                            dest="net_file")
        parser.add_argument("--emissions_file", type=str, default="emissions.xml",
                            help="The name of the SUMO emissions file.", dest="emissions_file")
        parser.add_argument("--weather_file", type=str, default="weather_data.txt",
                            help="The name of the weather data file.", dest="weather_file")
        parser.add_argument("--weather_day", type=str,
                            help="The day of the weather data to extract, format (dd.mm.yyyy)", dest="weather_day", default=None)
        parser.add_argument("--weather_hour", type=str,
                            help="The hour of the weather data to extract, format (hh:mm)", dest="weather_hour", default=None)
        parser.add_argument("--met_file", type=str, default="weather.met", help="The name of the met file.",
                            dest="met_file")
        parser.add_argument("--gral_exe", type=str, default="GRAL.exe",
                            help="The name of the GRAL executable.", dest="gral_exe")
        parser.add_argument("--osm_file", type=str, default=None,
                            help="The name of the OSM file.", dest="osm_file")

        args = parser.parse_args()

        main(args)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_cli()
