# SUMO2GRAL (S2G) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

S2G is a project aimed at simplifying the process of estimating pollutant concentrations in urban areas by automating the preparation of necessary files for simulation in [GRAL (Graz Lagrangian Model)](https://gral.tugraz.at/). By providing geographic area specifications, [SUMO (Simulation of Urban MObility) emissions files](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html), and weather data for the desired area, users can effortlessly generate the required files for conducting GRAL simulations. The weather data format aligns with the format provided by the [monitor stations of Valencian Environmental Agency](https://mediambient.gva.es/es/web/calidad-ambiental/datos-on-line).

## Features

- **Automated Data Processing**: Simplifies the preparation of input files for GRAL by automatically processing building, weather, highway, and map data.
- **Georeferenced Map Generation**: Creates georeferenced maps based on specified geographic bounds.
- **Shapefile Generation**: Generates shapefiles for buildings and highways which are essential for GRAL simulations.
- **Weather Data Processing**: Processes weather data to match the requirements of GRAL simulations.
- **GRAL Files Generation**: Automates the creation of required GRAL simulation files through a dedicated module.
- **GRAL Simulation**: Executes the GRAL simulation and outputs the reuslts in a .txt file.

## Prerequisites

You must have installed the Dotnet 6.0 SDK installed. Please visit the [Windows .NET 6.0 downloading page](https://dotnet.microsoft.com/en-us/download/dotnet/6.0). 

If you are a Linux user you can simply do:

```bash
sudo apt-get install -y dotnet-sdk-6.0
```

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

Offline mode (*default*):

- Parameters mode

  ```bash
  python cli.py --base-directory /path/to/base/directory --process all --osm-file /path/to/osm/file/file.osm  --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --gral-dll /path/to/gral/dll/file/GRAL.dll
  ```
- Configuration file mode (here you can take a look at the structure of the [config file](/examples/configuration.sumo2gral.cfg))

  ```bash
  python cli.py -c configuration.sumo2gral.cfg --process all
  ```



Online mode (This is in case you want to retrieve the data using the osmnx library):

```bash
python cli.py --base-directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --process all  --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --online --gral-dll /path/to/gral/dll/file/GRAL.dll
```

## Documentation

### Modules

- [`buildings/buildings_processor.py`](/buildings/buildings_processor.py): Processes building data to create shapefiles.
- [`weather/weather_processor.py`](/weather/weather_processor.py): Processes weather data to match the format required for GRAL simulations.
- [`line_emission_sources/highway_data_processor.py`](/line_emission_sources/highway_data_processor.py): Processes highway data to create shapefiles and processes SUMO emissions files.
- [`maps/maps_processor.py`](/maps/maps_processor.py): Generates georeferenced maps based on the specified geographic bounds.
- [`gral/gral_processor.py`](/gral/gral_processor.py): Automates the creation of required GRAL simulation files.
- [`local_files_processor/local_file_processor.py`](/local_files_processor/local_file_processor.py): Processes local files data to create shapefiles.
- [`main.py`](/main.py): Orchestrates the data processing based on user inputs.
- [`cli.py`](/cli.py): Provides a command line interface for the project.

### CLI Arguments

- `--base-directory`: The base directory for the project.
- `--north`, `--south`, `--east`, `--west`: The coordinates of the bounding box. (Default: None)
- `--epsg`: The EPSG code for the coordinate system to reproject the map to. (Must be different than EPSG:4326. **This is because GRAL does not support EPSG:4326.**) (Default:EPSG:3857)
- `--process`: Specify the process to run. Choices are: all, map, buildings, weather, highway, gral. (All does not include map, since the GRAL GUI is not used.)
- `--online`: Specify if the data is to be retrieved using the osmnx library. (Default: False)
- `--map-name`: The name of the map file to be saved.
- `--buildings-shp-file`: The name of the shapefile to be saved.
- `--highways-shp-file`: The name of the shapefile to be saved.
- `--net-file`: The name of the SUMO network file.
- `--emissions-file`: The name of the SUMO emissions file.
- `--weather-file`: The name of the weather data file.
- `--weather-day`: The day of the weather data to extract, format (dd.mm.yyyy).
- `--weather-hour`: The hour of the weather data to extract, format (hh:mm).
- `--met-file`: The name of the met file. (Default: weather.met)
- `--gral-dll`: The name of the GRAL dll file. (Required for GRAL simulations)
- `--pollutant`: The pollutant to be simulated. (Default: NOx)
- `--hor-layers`: The horizontal layers to be simulated (m.). (Default: 3,6,9)
- `--particles-ps`: The number of particles per second. (Default: 100)
- `--dispertion-time`: The dispertion time (s.). (Default: 3600)
- `--osm-file`: The name of the OSM file.

### Examples

- Generate a georeferenced map from the OSM file:

```bash
python cli.py --base-directory /path/to/base/directory  --process map --osm-file /path/to/osm/file/file.osm 
```

- Generate shapefile for buildings:

  - Retrieve data using the osmnx library

    ```bash
    python cli.py --base-directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --process buildings --online
    ```
  
  - Retrieve data using the local OSM file

    ```bash
    python cli.py --base-directory /path/to/base/directory --process buildings --osm-file /path/to/osm/file/file.osm
    ```

- Generate shapefile for line emission sources:

  - Retrieve data using the osmnx library

    ```bash
    python cli.py --base-directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process highway --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --online
    ```

  - Retrieve data using the local OSM file

    ```bash
    python cli.py --base-directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process highway --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --osm-file /path/to/osm/file/file.osm
    ```

- Generate the GRAL inputs and execute the simulation:

  - Without inputting the osm file

    ```bash
    python cli.py --base-directory /path/to/base/directory --north 39.50154 --south 39.4235 --east -0.30981 --west -0.44166 --process gral --met-file /path/to/met/file/metfile.met --online --gral-dll /path/to/gral/dll/file/GRAL.dll
    ```
  
  - Inputting the osm file

    ```bash
    python cli.py --base-directory /path/to/base/directory --process gral --met-file /path/to/met/file/metfile.met --osm-file /path/to/osm/file/file.osm --gral-dll /path/to/gral/dll/file/GRAL.dll
    ```

## GRAL Module Documentation

The `GRAL` class within the [`gral/gral_processor.py`](/gral/gral_processor.py) module serves to automate the creation of required files for GRAL simulation based on user inputs and predefined values. Below is an outline of its structure and functionalities:

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
        create_meteopgt_file(): Creates a meteopgt.all file with predefined values.
        create_pollutant_txt_file(pollutant): Creates a pollutant.txt file with predefined values.
        create_percent_file(): Creates a Percent.txt file with predefined values.
        create_max_proc_file(n_cores): Creates a Max_Proc.txt file with predefined values.
        create_other_txt_requiered_files(pollutant, n_cores): Creates the other txt requiered files with predefined values.
        create_buildings_file(): Creates a buildings.dat file with predefined values.
        create_line_emissions_file(pollutant): Creates a line.dat file with predefined values.
        create_met_time_series_data_file(meteo_file): Creates a mettimeseries.dat file with predefined values.
        create_dispersion_number_file(): Creates a DispNr.txt file with predefined values.
        create_other_optional_files(): Creates the other optional files with predefined values.
        get_number_of_weather_conditions(): Gets the number of weather conditions.
        rename_results(pollutant, horizontal_layers, n_meteo_conditions): Rename the results files.
        check_pollutant(pollutant): Checks if the pollutant is valid.
        check_horizontal_layers(horizontal_layers): Checks if the horizontal layers are valid.
    """
    ...

```

## Contributing

Contributions are welcome! Create a new issue to discuss a feature or bug, or create a pull request to propose changes.

## License

This project is licensed under the [MIT License](LICENSE).
