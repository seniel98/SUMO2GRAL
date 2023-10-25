# SUMO2GRAL (S2G) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

S2G is a project aimed at simplifying the process of estimating pollutant concentrations in urban areas by automating the preparation of necessary files for simulation in [GRAL (Graz Lagrangian Model)](https://gral.tugraz.at/). By providing geographic area specifications, [SUMO (Simulation of Urban MObility) emissions files](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html), and weather data for the desired area, users can effortlessly generate the required files for conducting GRAL simulations. The weather data format aligns with the format provided by the [monitor stations of Valencian Environmental Agency](https://mediambient.gva.es/es/web/calidad-ambiental/datos-on-line).

## Features

- **Automated Data Processing**: Simplifies the preparation of input files for GRAL by automatically processing building, weather, highway, and map data.
- **Georeferenced Map Generation**: Creates georeferenced maps based on specified geographic bounds.
- **Shapefile Generation**: Generates shapefiles for buildings and highways which are essential for GRAL simulations.
- **Weather Data Processing**: Processes weather data to match the requirements of GRAL simulations.
- **GRAL Files Generation**: Automates the creation of required GRAL simulation files through a dedicated module.

## Dependencies

- pandas
- osmnx
- sumolib
- numpy
- geopandas
- cartopy
- pyproj
- osmium

## Setup

Clone the repository:

```bash
git clone https://github.com/seniel98/SUMO2GRAL.git
cd SUMO2GRAL
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the command line interface (CLI) script with the desired arguments to process the data and generate the required files:

```bash
python CLI.py --base_directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --epsg 3857 --process all  --net_file /path/to/net/file/file.net.xml --emissions_file /path/to/edge/emissions/file/edges_emisisons_file.csv 
```

## Documentation

### Modules

- `buildings/buildings_processor.py`: Processes building data to create shapefiles.
- `weather/weather_processor.py`: Processes weather data to match the format required for GRAL simulations.
- `line_emission_sources/highway_data_processor.py`: Processes highway data to create shapefiles and processes SUMO emissions files.
- `maps/maps_processor.py`: Generates georeferenced maps based on the specified geographic bounds.
- `gral/gral_files_generator.py`: Automates the creation of required GRAL simulation files.
- `local_files_processor/local_file_processor.py`: Processes local files data to create shapefiles.
- `main.py`: Orchestrates the data processing based on user inputs.
- `cli.py`: Provides a command line interface for the project.

### CLI Arguments

- `--base_directory`: The base directory for the project.
- `--north`, `--south`, `--east`, `--west`: The coordinates of the bounding box.
- `--epsg`: The EPSG code for the coordinate system to reproject the map to. (Must be different than EPSG:4326. **This is because GRAL does not support EPSG:4326.**) (Default:EPSG:3857)
- `--process`: Specify the process to run. Choices are: map, buildings, buildings offline ,weather, highway, highway offline, gral, gral offline, all. (Note: All does not include gral)
- `--map_name`: The name of the map file to be saved.
- `--buildings_shp_file`: The name of the shapefile to be saved.
- `--highways_shp_file`: The name of the shapefile to be saved.
- `--net_file`: The name of the SUMO network file.
- `--emissions_file`: The name of the SUMO emissions file.
- `--weather_file`: The name of the weather data file.
- `--weather_day`: The day of the weather data to extract, format (dd.mm.yyyy).
- `--weather_hour`: The hour of the weather data to extract, format (hh:mm).
- `--met_file`: The name of the met file. (Default: weather.met)
- `--gral_exe`: The name of the GRAL executable. (Default: GRAL.exe)
- `--osm_file`: The name of the OSM file.

### Examples

- Generate a georeferenced map of the specified geographic bounds:

```bash
python cli.py --base_directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --epsg 3857 --process map
```

- Generate shapefile for buildings:

  - Retrieve data using the osmnx library

    ```bash
    python cli.py --base_directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --epsg 3857 --process buildings --buildings_shp_file /path/to/buildings/shp/file/file.shp
    ```
  
  - Retrieve data using the local OSM file

    ```bash
    python cli.py --base_directory /path/to/base/directory --epsg 3857 --process "buildings offline" --osm_file /path/to/osm/file/file.osm --buildings_shp_file /path/to/buildings/shp/file/file.shp
    ```

- Generate shapefile for line emission sources:

  - Retrieve data using the osmnx library

    ```bash
    python cli.py --base_directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process highway --net_file /path/to/net/file/file.net.xml --emissions_file /path/to/edge/emissions/file/edges_emisisons_file.csv
    ```

  - Retrieve data using the local OSM file

    ```bash
    python cli.py --base_directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process "highway offline" --net_file /path/to/net/file/file.net.xml --emissions_file /path/to/edge/emissions/file/edges_emisisons_file.csv --osm_file /path/to/osm/file/file.osm --highways_shp_file /path/to/highways/shp/file/file.shp
    ```

- Generate the GRAL.exe inputs

  - Without inputting the osm file

    ```bash
    python cli.py --base_directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process gral --met_file /path/to/met/file/metfile.met
    ```
  
  - Inputting the osm file

    ```bash
    python cli.py --base_directory /path/to/base/directory --process "gral offline" --met_file /path/to/met/file/metfile.met --osm_file /path/to/osm/file/file.osm
    ```

## GRAL Module Documentation

The `GRAL` class within the `gral/gral_files_generator.py` module serves to automate the creation of required files for GRAL simulation based on user inputs and predefined values. Below is an outline of its structure and functionalities:

```python
class GRAL:
    """
    A class used to represent the GRAL module.

    Attributes:
        base_directory (str): The base directory for the project.
        met_file (str): The name of the met file.
        buildings_file (str): The name of the buildings file.
        line_file (str): The name of the line file.

    Methods:
        create_greb_file(bbox, horizontal_slices): Creates a GREB file with predefined values.
        create_in_dat_file(particles_ps, dispertion_time, latitude, horizontal_slices): Creates a in.dat file with predefined values.
        create_meteogpt_file(): Creates a meteogpt.all file with predefined values.
        create_pollutant_txt_file(pollutant): Creates a pollutant.txt file with predefined values.
        create_percent_file(): Creates a Percent.txt file with predefined values.
        create_max_proc_file(n_cores): Creates a Max_Proc.txt file with predefined values.
        create_other_txt_requiered_files(pollutant, n_cores): Creates the other txt requiered files with predefined values.
        create_buildings_file(): Creates a buildings.dat file with predefined values.
        create_line_emissions_file(pollutant): Creates a line.dat file with predefined values.
        create_met_time_series_data_file(meteo_file): Creates a mettimeseries.dat file with predefined values.
        create_dispersion_number_file(): Creates a DispNr.txt file with predefined values.
        create_other_optional_files(): Creates the other optional files with predefined values.
    """
    ...

```

## Contributing

Contributions are welcome! Create a new issue to discuss a feature or bug, or create a pull request to propose changes.

## License

This project is licensed under the [MIT License](LICENSE).
